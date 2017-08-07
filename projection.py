import numpy
import json
from tkinter import *

__author__ = 'https://github.com/rafaiska'

OBJJSONPATH = 'objeto.json'


mainframe = Tk()
mainframe.geometry("800x600+0+150")
mainframe.wm_title("3kaD: Sistema de visualização de objetos 3D")

frameCanvas = Frame(mainframe, borderwidth=4, relief=GROOVE)
frameCanvas.pack(side=LEFT, expand=True, fill=BOTH)

scrollcanvasx = Scrollbar(frameCanvas, orient=HORIZONTAL)
scrollcanvasx.pack(side=BOTTOM, fill=X)
scrollcanvasy = Scrollbar(frameCanvas)
scrollcanvasy.pack(side=RIGHT, fill=Y)
canvas = Canvas(frameCanvas, bg="black", scrollregion=(-1000,-1000,2000,2000), xscrollcommand=scrollcanvasx.set, yscrollcommand=scrollcanvasy.set, width=670, height=590)
scrollcanvasx.config(command=canvas.xview)
scrollcanvasy.config(command=canvas.yview)
canvas.pack(side=LEFT, expand=True, fill=BOTH)

#botaoAbrir = Button(mainframe, width=8, borderwidth=2, text="Abrir")
#botaoAbrir.place(x=40, y=20)


class TriDObject(object):
    """Essa classe serve para representar uma figura espacial atraves de vertices e arestas, os quais estao em um
    espaco de coordenadas do mundo (WCS). Os vertices e as arestas sao representadas da seguinte forma:

    self.vertices: uma lista contendo tuplas (NOME_DO_VERTICE, X, Y, Z), onde NOME_DO_VERTICE eh uma string, X, Y e Z
    sao coordenadas espaciais em ponto flutuante

    self.edges: um dicionario cujas chaves sao vertices da figura, construidos como no formato acima. Cada chave
    referencia uma lista de vertices, os quais formam adjacencia com o vertice chave. Na pratica, no contexto de
    estrutura de dados, esse dicionario eh uma matriz de adjacencia de um grafo."""
    def __init__(self):
        self.vertices = []
        self.edges = {}
        self.faces = {}

    def get_vertix(self, name):
        for vertix in self.vertices:
            if vertix[0] == name:
                return vertix
        return None

    def loadfromjson(self, jsonpath):
        """Carrega a figura 3D descrita no arquivo json"""
        with open(jsonpath, 'r') as objfile:
            loadedjson = json.load(objfile)
            objfile.close()

        for vertix, coord in loadedjson['vertices'].items():
            self.addvertix(vertix, coord[0], coord[1], coord[2])

        for src, dsts in loadedjson['edges'].items():
            for dst in dsts:
                self.addedge(src, dst)

        for facename, verticeslist in loadedjson['faces'].items():
            self.addface(facename, verticeslist)

    def loadfromnumpymatrix(self, parenttridobject, numpymatrix):
        """Carrega o objeto 3D a partir de uma matriz de pontos e um objeto 3D de referencia. Eh necessario passar um
        objeto de referencia para que se conheca as arestas do objeto, que nao sao representadas nas matrizes de objeto
        utilizadas nas operacoes matematicas de projecao"""
        if not isinstance(parenttridobject, TriDObject):
            raise AttributeError('Parametro parenttridobject precisa ser objeto da classe TriDObject')
        verticesnames = []

        for vertix in parenttridobject.vertices:
            verticesnames.append(int(vertix[0]))

        j = 0
        for vertix in sorted(verticesnames):
            # numpymatrix[3, j] eh o valor da coordenada w (coordenadas homogeneas). Divide-se por ele para obter as
            # coordenadas reais de x, y e z
            self.addvertix(vertix,
                           float(numpymatrix[0, j]) / float(numpymatrix[3, j]),
                           float(numpymatrix[1, j]) / float(numpymatrix[3, j]),
                           float(numpymatrix[2, j]) / float(numpymatrix[3, j]))
            j += 1

        self.edges = parenttridobject.edges
        self.faces = parenttridobject.faces

    def addvertix(self, name, x, y, z):
        """Adiciona um vertice"""
        self.vertices.append((name, x, y, z))

    def addedge(self, vertixa_name, vertixb_name):
        """Adiciona uma aresta"""
        if vertixa_name not in self.edges.keys():
            self.edges[vertixa_name] = []
        if vertixb_name not in self.edges.keys():
            self.edges[vertixb_name] = []
        if vertixb_name not in self.edges[vertixa_name]:
            self.edges[vertixa_name].append(vertixb_name)
        if vertixa_name not in self.edges[vertixb_name]:
            self.edges[vertixb_name].append(vertixa_name)

    def addface(self, facename, vertices_names):
        """Adiciona uma aresta"""
        self.faces[facename] = vertices_names

    def removeface(self, facename):
        del self.faces[facename]
        self.updatevertices()

    def updatevertices(self):
        def notpartofanyface(vertixname):
            for face in self.faces.values():
                if vertixname in face:
                    return False
            return True

        # Seleciona para remocao vertices que nao aparecam em mais nenhuma face da figura
        removevertixlist = []
        for vertix in self.vertices:
            if notpartofanyface(vertix[0]):
                removevertixlist.append(vertix)
                del self.edges[vertix[0]]

        # Remove arestas que contem vertices a serem removidos
        for dsts in self.edges.values():
            for vertix in removevertixlist:
                if vertix[0] in dsts:
                    dsts.remove(vertix[0])

        # Remove todos os vertices listados para remocao
        for vertix in removevertixlist:
            self.vertices.remove(vertix)

    def numpymatrix(self):
        xrow = []
        yrow = []
        zrow = []
        wrow = [1] * len(self.vertices) # Coordenadas homogeneas possuem w. Nessa conversao, w=1 para todas coordenadas
        for vertix in sorted(self.vertices, key=lambda vertix: vertix[0]):
            xrow.append(vertix[1])
            yrow.append(vertix[2])
            zrow.append(vertix[3])
        return numpy.matrix([xrow, yrow, zrow, wrow])



class PerspectiveProjection(object):
    def __init__(self):
        self.tridiobject = None
        self.projection = None

    def loadtridiobject(self, objectpath=OBJJSONPATH):
        self.tridiobject = TriDObject()
        self.tridiobject.loadfromjson(objectpath)

    def tridiobjecttranslation(self, coordinates):
        """Translada o objeto carregado em self.tridiobject de acordo com as coordenadas de translacao passadas por
        parametro. Coordinates deve ser uma tupla do tipo (x, y, z)"""
        if not self.tridiobject:
            return False

        dx = coordinates[0]
        dy = coordinates[1]
        dz = coordinates[2]

        translationmatrix = [[1, 0, 0, dx],
                             [0, 1, 0, dy],
                             [0, 0, 1, dz],
                             [0, 0, 0, 1]]
        translationmatrix = numpy.matrix(translationmatrix)
        results = translationmatrix * self.tridiobject.numpymatrix()
        newtridiobject = TriDObject()
        newtridiobject.loadfromnumpymatrix(self.tridiobject, results)
        self.tridiobject = newtridiobject
        return True

    def perspectivematrix(self, pointofview):
        """Calcula a matriz perspectiva considerando o plano de projecao em Z=0. O ponto de vista PV(a,b,c) eh passado
        como parametro do metodo em forma de uma tupla (a, b, c)
        a = pointofview[0]
        b = pointofview[1]
        c = pointofview[2]"""

        # Primeiro passo: calcular vetor normal ao plano de projecao. Como o plano de projecao eh Z=0, o vetor eh o
        # versor k, paralelo ao eixo Z

        nx = 0
        ny = 0
        nz = 1

        # Segundo passo: calcular d0 a partir de um ponto (x0, y0, z0) em cima do plano de projecao. Escolhe-se o ponto
        # (0,0,0) para facilitar os calculos
        # d0 = x0 * nx + y0 * ny + z0 * nz = 0 * 0 + 0 * 0 + 0 * 1 = 0

        d0 = 0

        # Terceiro passo: calcular d1, que depende dos dados do plano de projecao e do ponto de vista

        d1 = pointofview[0] * nx + pointofview[1] * ny + pointofview[2] * nz

        # Quarto passo: calculo de d, dado simplesmente por d0 - d1

        d = d0 - d1

        # Quinto passo: montar a matriz de projecao com os dados calculados
        # A matriz eh uma lista de listas na qual cada lista interior eh uma linha da matriz

        returnmatrix = [[d + pointofview[0] * nx, pointofview[0] * ny, pointofview[0] * nz, - pointofview[0] * d0],
                        [pointofview[1] * nx, d + pointofview[1] * ny, pointofview[1] * nz, - pointofview[1] * d0],
                        [pointofview[2] * nx, pointofview[2] * ny, d + pointofview[2] * nz, - pointofview[2] * d0],
                        [nx, ny, nz, - d1]]

        # Retorna uma matriz do pacote numpy, construida a partir da matriz construida acima. As matrizes do numpy
        # permitem utilizar facilmente operacoes basicas de matrizes sobre elas, como a multiplicacao
        return numpy.matrix(returnmatrix)

    def getprojection(self, pointofview):
        """Esse metodo recebe uma tupla (X, Y, Z) como parametro, o qual representa as coordenadas do ponto de vista
        utilizado na projecao. O metodo retorna um objeto do tipo TriDObject, que esta descrito acima, no docstring de
        sua respectiva classe.

        O objeto TriDObject de retorno possui vertices e arestas contidos no plano de projecao Z=0, o que implica que
        ele forma uma figura em duas dimensoes (2D). Essa figura deve ser construida em uma tela de pintura do Tkinter
        ou similar, com coordenadas do display utilizado para exibicao"""
        if not self.tridiobject:
            self.loadtridiobject()

        #hiddenfaces = self.detecthiddenfaces(pointofview)
        perspectivematrix = self.perspectivematrix(pointofview)
        results = perspectivematrix * self.tridiobject.numpymatrix()
        self.projection = TriDObject()
        self.projection.loadfromnumpymatrix(self.tridiobject, results)
        #for face in hiddenfaces:
        #    self.projection.removeface(face)

        # Retorna o TriDObject de projecao, armazenado no atributo da classe
        return self.projection


Sx = 800/20 # 40
Sy = 600/15 # 40


projection = PerspectiveProjection()
projecaoEscada = projection.getprojection((8,2,10))
print(len(projecaoEscada.vertices))
print(projecaoEscada.vertices)

i=0;j=1; k=0; l=0;m=0;n=0; cont=0; valor=0
Tjv = [[Sx, 0, 600], [0, Sy, 280], [0, 0, 1]]
matrizResultante = [[],[],[]]


def janelaViewport():
    global projecaoEscada, matrizResultante, Tjv, i,j,k,l,m,n,cont,valor
    while True:
        #print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK: " + str(k))
        for i in range(len(projecaoEscada.vertices)-1):
            if(n==12):
                #print("ENTREI NO IF ")
                n=0
                k+=1
                m+=1
                #cont+=1
            l=0
            for j in range(3):
                #print("\nTjv[" + str(k)+"][" + str(l) + "]:" + str(Tjv[k][l]))
                #print("\nvertices[" + str(k)+"][" + str(l) + "]: " + str(projecaoEscada.vertices[i][j]))
                valor = Tjv[k][l] * projecaoEscada.vertices[i][j]
                #print("\nvalor: " + str(valor))
                l+=1
                matrizResultante[m].append(valor)
                #print(matrizResultante)
                #print(cont)
                n+=1
                if(cont==35):
                    print("RETORNEI PORRA!")
                    print(matrizResultante)
                    return
                cont+=1

janelaViewport()

#print(matrizResultante)
print(canvas.create_polygon(matrizResultante[0][0], matrizResultante[1][0], matrizResultante[0][1],
                            matrizResultante[1][1], matrizResultante[0][2], matrizResultante[1][2],
                            matrizResultante[0][3], matrizResultante[1][3], matrizResultante[0][4], matrizResultante[1][4], outline="green"))



mainloop()
