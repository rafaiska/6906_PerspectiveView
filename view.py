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

class InputFrame(tkinter.Frame):
    def __init__(self, root):
        tkinter.Frame.__init__(self, master=root)
        self.root = root
        self.entryx = tkinter.Entry(master=self)
        self.entryy = tkinter.Entry(master=self)
        self.entryz = tkinter.Entry(master=self)
        self.labelentryx = tkinter.Label(master=self, text='X:')
        self.labelentryy = tkinter.Label(master=self, text='Y:')
        self.labelentryz = tkinter.Label(master=self, text='Z:')
        self.projectbutton = tkinter.Button(master=self, text='Projetar')
        self.entryx.grid(row=0, column=1)
        self.entryy.grid(row=0, column=3)
        self.entryz.grid(row=0, column=5)
        self.labelentryx.grid(row=0, column=0)
        self.labelentryy.grid(row=0, column=2)
        self.labelentryz.grid(row=0, column=4)
        self.projectbutton.grid(row=0, column=6)
        self.projectbutton.bind('<Button-1>', self.projectobject)

    def projectobject(self, event):
        try:
            projx = float(self.entryx.get())
        except ValueError:
            projx = 0.0
        try:
            projy = float(self.entryy.get())
        except ValueError:
            projy = 0.0
        try:
            projz = float(self.entryz.get())
        except ValueError:
            projz = 0.0
        self.root.canvas.delete('all')
        danteprojection = projection.PerspectiveProjection()
        projected = danteprojection.getprojection((projx, projy, projz))
        mainview.drawprojection(projected)

class MainView(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title('Projecao3D')
        self.canvas = tkinter.Canvas(master=self, width=MSCREEN_WIDTH, height=MSCREEN_HEIGHT, bg="black")
        self.canvas.pack(expand=True, fill="x")
        self.inputframe = InputFrame(self)
        self.inputframe.pack()

    def drawedge(self, edge):
        srcx = int(edge[0][1])
        srcy = int(edge[0][2])
        dstx = int(edge[1][1])
        dsty = int(edge[1][2])
        self.canvas.create_line(srcx, srcy, dstx, dsty, fill="green")

    def drawprojection(self, projected):
        # achar x e y minimos
        minx, miny = get_minxy(projected)

        # trazer esse retangulo para a origem
        originprojected = projected.translation((0 - minx, 0 - miny, 0))

        # refletir no plano xz
        mirrorprojected = originprojected.xzmirror()

        # repetir os dois primeiros passos
        minx, miny = get_minxy(mirrorprojected)
        originprojected = mirrorprojected.translation((0 - minx, 0 - miny, 0))

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

        # centralizar
        maxx, maxy = get_maxxy(scaleprojected)
        if maxx < MSCREEN_WIDTH -1:
            #print('maxx = %f' % (maxx))
            scaleprojected = scaleprojected.translation(((MSCREEN_WIDTH - maxx) / 2.0, 0, 0))
        if maxy < MSCREEN_HEIGHT -1:
            #print('maxy = %f' % (maxy))
            scaleprojected = scaleprojected.translation((0, (MSCREEN_HEIGHT - maxy) / 2.0, 0))

        # desenhar arestas
        drawnedges = [] # para nao desenhar a mesma aresta duas vezes
        for src, dsts in scaleprojected.edges.items():
            for dst in dsts:
                if (dst, src) not in drawnedges:
                    self.drawedge((scaleprojected.get_vertix(src), scaleprojected.get_vertix(dst)))

if __name__ == "__main__":
    mainview = MainView()
    mainview.mainloop()
