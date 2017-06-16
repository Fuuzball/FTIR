from __future__ import division
import Tkinter as tk
import numpy as np

rg = 0

imgW = 607
imgH = 295

Xpts = 108
Ypts = 53


def keyPress(event):
    if event.char == 'x':
        rg = 1 - rg

class regionSelectGUI:
    def __init__(self, root, imgPath):
        self.root = root
        root.title('Select region of interest')

        self.addRegion = True
        self.brushSize = 10

        self.ptsInt = np.zeros((Xpts, Ypts))
        self.scanPoints = [ [0 for _ in range(Ypts)] for _ in range(Xpts)]

        # Create canvas
        self.canvas = tk.Canvas(root, width = imgW, height = imgH)

        self.canvas.pack()

        # Load image as background
        self.img = tk.PhotoImage(file = imgPath) 
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.img) 

        # Listen for Key and mouse events
        self.canvas.bind("<B1-Motion>", self.paint) 
        self.canvas.bind("<Key>", self.keyPress) 

        self.initializePoints()

    def paint(self, event):
        self.canvas.focus_set()
        if self.addRegion:
            color = "#008000" #Green
        else:
            color = "#800000" #Red
        r = self.brushSize
        x1, y1 = (event.x - r), (event.y - r)
        x2, y2 = (event.x + r), (event.y + r)
        self.canvas.create_oval(x1, y1, x2, y2, fill = color, width = 0)

        self.addPoints(event.x, event.y)
        self.updatePoints()
        #self.colorPoints()

    def initializePoints(self):
        for i in range(Xpts):
            for j in range(Ypts):
                x = imgW/(Xpts - 1) * i
                y = imgH/(Ypts - 1) * j
                r = 1
                self.scanPoints[i][j] = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill = "#0000FF", width = 0)

    def keyPress(self, event):
        if event.char == 'x':
            #Switch from adding to taking away
            self.addRegion = not self.addRegion

    def addPoints(self, x0, y0):
        r = self.brushSize
        for x in range(x0 - r, x0 + r):
            ymin = y0 - np.round( np.sqrt(r**2 - (x - x0)**2))
            ymax = y0 + np.round( np.sqrt(r**2 - (x - x0)**2))
            ymin = int(ymin)
            ymax = int(ymax)
            
            for y in range(ymin, ymax):
                i, j = self.getNearestPoint(x, y)
                if self.addRegion:
                    self.ptsInt[i, j] = 1
                else:
                    self.ptsInt[i, j] = -1

    def updatePoints(self):
        for i in range(Xpts):
            for j in range(Ypts):
                if self.ptsInt[i, j] == 1:
                    self.canvas.itemconfig(
                            self.scanPoints[i][j], fill = "green"
                            )
                    self.canvas.tag_raise(
                        self.scanPoints[i][j]
                            )

                if self.ptsInt[i, j] == -1:
                    self.canvas.itemconfig(
                            self.scanPoints[i][j], fill = "red"
                            )
                    self.canvas.tag_raise(
                        self.scanPoints[i][j]
                            )


                
    def getNearestPoint(self, x, y):
        i = int(np.round(x * (Xpts - 1) / imgW))
        j = int(np.round(y * (Ypts - 1) / imgH))
        return i, j


imgPath = './data/vis_img.gif'
root = tk.Tk()
my_gui = regionSelectGUI(root, imgPath)
root.mainloop()

