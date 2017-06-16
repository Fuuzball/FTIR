import Tkinter as tk
import numpy as np

rg = 0

imgW = 608
imgH = 296


def keyPress(event):
    if event.char == 'x':
        rg = 1 - rg

class regionSelectGUI:
    def __init__(self, root, imgPath):
        self.root = root
        root.title('Select region of interest')

        self.addRegion = True

        regionOfInterest = np.zeros(())

        # Create canvas
        self.canvas = tk.Canvas(root, width = imgW, height = imgH)

        # Load image as background
        self.img = tk.PhotoImage(file = imgPath) 
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.img) 

        # Listen for Key and mouse events
        self.canvas.bind("<B1-Motion>", self.paint) 
        self.canvas.bind("<Key>", self.keyPress) 
        
        self.canvas.pack()

    def paint(self, event, r = 10):
        self.canvas.focus_set()
        if self.addRegion:
            color = "#008000" #Green
        else:
            color = "#800000" #Red
        x1, y1 = (event.x - r), (event.y - r)
        x2, y2 = (event.x + r), (event.y + r)
        self.canvas.create_oval(x1, y1, x2, y2, fill = color, width = 0)

    def keyPress(self, event):
        if event.char == 'x':
            #Switch from adding to taking away
            self.addRegion = not self.addRegion


        

        
        
        

imgPath = './data/vis_img.gif'
root = tk.Tk()
my_gui = regionSelectGUI(root, imgPath)
root.mainloop()

