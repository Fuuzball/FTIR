import OMNIC_interface as Om
from box_select import boxSelect
import Tkinter as tk
import numpy as np
from PIL import Image
from PIL import ImageTk

imgPath = './data/vis_img_select.JPG'

a = 567 / 200
b = 425 / 150
x1, y1 = 400, -10250
u1, v1 = 630, 294
x0 = (x1 - u1/a)
y0 = (y1 - v1/b)

def printf(s):
    print(s)

root = tk.Tk()
my_gui = boxSelect(root, imgPath, a, b, x0, y0, printf)

