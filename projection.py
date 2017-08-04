import numpy

OBJJSONPATH = 'objeto.json'

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

    def loadfromjson(self, jsonpath):
        """Carrega a figura 3D descrita no arquivo json"""
        pass

class PerspectiveProjection(object):
    def __init__(self):
        self.tridiobject = None
        self.projection = None

    def loadtridiobject(self):
        self.tridiobject = TriDObject()
        self.tridiobject.loadfromjson(OBJJSONPATH)

    def getprojection(self, pointofview):
        """Esse metodo recebe uma tupla (X, Y, Z) como parametro, o qual representa as coordenadas do ponto de vista
        utilizado na projecao. O metodo retorna um objeto do tipo TriDObject, que esta descrito acima, no docstring de
        sua respectiva classe.

        O objeto TriDObject de retorno possui vertices e arestas contidos no plano de projecao Z=0, o que implica que
        ele forma uma figura em duas dimensoes (2D). Essa figura deve ser construida em uma tela de pintura do Tkinter
        ou similar, com coordenadas do display utilizado para exibicao"""
        if not self.tridiobject:
            self.loadtridiobject()

        # FAZER OPERACOES DE PROJECAO AQUI

        # Retorna o TriDObject de projecao, armazenado no atributo da classe
        return self.projection