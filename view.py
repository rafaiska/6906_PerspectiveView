import tkinter
import projection
import math

MSCREEN_HEIGHT = 600
MSCREEN_WIDTH = 800

def get_minxy(projected):
    minx = math.inf
    miny = math.inf


    for vertix in projected.vertices:
        if vertix[1] < minx:
            minx = vertix[1]

        if vertix[2] < miny:
            miny = vertix[2]


    return minx, miny

def get_maxxy(projected):
    maxx = - math.inf
    maxy = - math.inf

    for vertix in projected.vertices:
        if vertix[1] > maxx:
            maxx = vertix[1]

        if vertix[2] > maxy:
            maxy = vertix[2]

    return maxx, maxy


class MainView(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.canvas = tkinter.Canvas(master=self, width=MSCREEN_WIDTH, height=MSCREEN_HEIGHT)
        self.canvas.pack()

    def drawedge(self, edge):
        srcx = int(edge[0][1])
        srcy = int(edge[0][2])
        dstx = int(edge[1][1])
        dsty = int(edge[1][2])
        self.canvas.create_line(srcx, srcy, dstx, dsty)

    def drawprojection(self, projected):
        # achar x e y minimos
        minx, miny = get_minxy(projected)

        # trazer esse retangulo para a origem
        originprojected = projected.translation((0 - minx, 0 - miny, 0))

        # achar x e y maximos do objeto transladado
        maxx, maxy = get_maxxy(originprojected)

        # verificar taxa de escala
        xrate = MSCREEN_WIDTH / maxx
        yrate = MSCREEN_HEIGHT / maxy
        if xrate > yrate:
            xrate = yrate
        else:
            yrate = xrate

        # mudar escala
        scaleprojected = originprojected.scale((xrate, yrate, 1.0))

        # desenhar arestas
        drawnedges = [] # para nao desenhar a mesma aresta duas vezes
        for src, dsts in scaleprojected.edges.items():
            for dst in dsts:
                if (dst, src) not in drawnedges:
                    print(src)
                    print(dst)
                    self.drawedge((scaleprojected.get_vertix(src), scaleprojected.get_vertix(dst)))

if __name__ == "__main__":
    mainview = MainView()
    danteprojection = projection.PerspectiveProjection()
    projected = danteprojection.getprojection((8,2,10))
    mainview.drawprojection(projected)
    mainview.mainloop()
