from __future__ import division
import Tkinter as tk
import numpy as np
from region_select_GUI import regionSelectGUI

imgPath = './data/vis_img.gif'
root = tk.Tk()

imgW = 607
imgH = 295

Xpts = 108
Ypts = 53

imgSize = (imgW, imgH)
pointsDim = (Xpts, Ypts)
my_gui = regionSelectGUI(root, imgPath, imgSize, pointsDim)
root.mainloop()
