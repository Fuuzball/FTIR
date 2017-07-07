from __future__ import division
import Tkinter as tk
import numpy as np
from PIL import Image
from PIL import ImageTk

def classifyPoints(points, spec):
    X0 = []
    X1 = []
    y0 = []
    y1 = []
    for i, j in np.argwhere(points == -1):
        X0.append(spec[i,j])
        y0.append(0)
    for i, j in np.argwhere(points == 1):
        X1.append(spec[i,j])
        y1.append(1)

    X = np.vstack((X0, X1))
    y = np.hstack((y0, y1))

    clf = svm.SVC(kernel = 'linear')
    clf.fit(X, y)

    specList = spec.reshape(-1, spec.shape[-1])
    pred = clf.predict(specList)
    predXY = pred.reshape(points.shape)
    plt.imshow(predXY)
    plt.show()
   
def classifyPointsref(points, spec):
    print (points.shape)
    print (spec.shape)
    #print(np.argwhere(points == 1))

    [spec[idx] for idx in np.where(points == 1)]
    X0 = spec[np.argwhere(points == -1)]
    X1 = sepc[np.argwhere(points == 1)]
    X = np.vstack((X0, X1))
    y = np.ones(X.shape[0])
    y[:X0.shape[0]] = 0

    clf = svm.SVC(kernel = 'linear')
    clf.fit(X, y)

class boxSelect:
    def __init__(self, root, imgPath, a, b, x0, y0, scanPtsFn):
        self.root = root
        self.scanFn = scanPtsFn

        # Load reference image
        self.img = Image.open(imgPath)

        imgW = self.img.width
        imgH = self.img.height
        self.a = a
        self.b = b
        self.x0 = x0
        self.y0 = y0 

        self.deltaX = 5
        self.snapx0 = 0
        self.snapy0 = 0
        self.pointsToScan = []

        # Create canvas
        self.canvas = tk.Canvas(root, width = imgW, height = imgH)
        self.canvas.pack()

        self.pointsDrawn = []

        # Load image as background
        self.photo = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.photo)

        self.rectDrag = None

        # Listen for key and mosue events
        self.canvas.bind("<ButtonPress-1>", self.mouseDown)
        self.canvas.bind("<B1-Motion>", self.mouseMove)
        self.canvas.bind("<ButtonRelease-1>", self.mouseUp)
        self.canvas.bind("<Key>", self.keyPress)

    def keyPress(self, event):
        if event.char == 's':
            self.scanFn(self.pointsToScan)

    def mouseDown(self, event):
        self.canvas.focus_set()
        u, v = self.snapUV(event.x, event.y)
        self.u0, self.v0 = u, v

        self.cleanDrawinig()
        self.rectDrag = self.canvas.create_rectangle(self.u0, self.v0, self.u0, self.v0, outline = "red") 

    def cleanDrawinig(self):
        self.canvas.delete(self.rectDrag)
        for oval in self.pointsDrawn:
            self.canvas.delete(oval)
        self.pointsDrawn = []

    def mouseMove(self, event):
        self.u, self.v = self.snapUV(event.x, event.y)
        self.canvas.coords(self.rectDrag, self.u0, self.v0, self.u, self.v)

    def mouseUp(self, event):
        self.pointsToScan = self.getPointsEnclosed(self.u0, self.v0, self.u, self.v)
        self.drawPointsEncl(self.pointsToScan)

    def uv_to_xy(self, u, v):
        x = u / self.a + self.x0
        y = v / self.b + self.y0
        return x, y

    def xy_to_uv(self, x, y):
        u = (x - self.x0) * self.a
        v = (y - self.y0) * self.b
        return u, v

    def snapUV(self, u, v):
        x, y = self.uv_to_xy(u, v)
        x = (x // self.deltaX) * self.deltaX 
        y = (y // self.deltaX) * self.deltaX
        return self.xy_to_uv(x, y)

    def getPointsEnclosed(self, u1, v1, u2, v2):
        if u1 > u2:
            u2, u1 = u1, u2
        if v1 > v2:
            v2, v1 = v1, v2
        x1, y1 = self.uv_to_xy(u1, v1)
        x2, y2 = self.uv_to_xy(u2, v2)

        x1 = (x1 // self.deltaX) * self.deltaX
        y1 = (y1 // self.deltaX) * self.deltaX
        x2 = (x2 // self.deltaX + 1) * self.deltaX
        y2 = (y2 // self.deltaX + 1) * self.deltaX 

        xList = np.arange(x1, x2, self.deltaX)
        yList = np.arange(y1, y2, self.deltaX)

        return [(x, y) for x in xList for y in yList]

    def drawPointsEncl(self, pointsEncl):
        for xy in pointsEncl:
            x, y = xy
            u, v = self.xy_to_uv(x, y)
            r = 1
            self.pointsDrawn.append(
                    self.canvas.create_oval(u - r, v - r, u + r, v + r, fill = 'red', outline = '')
                    )

        
#specFile = './data/test.hdr'
#lib = envi.open(specFile)
#spec = np.array(lib[:,:,:])
#spec = np.flipud(spec)

imgPath = './data/vis_img_select.JPG'

a = 567 / 200
b = 425 / 150
x1, y1 = 400, -10250
u1, v1 = 630, 294
x0 = (x1 - u1/a)
y0 = (y1 - v1/b)

root = tk.Tk()
def printfn(scanPts):
    print (scanPts)
my_gui = boxSelect(root, imgPath, a, b, x0, y0, printfn)
root.mainloop()
