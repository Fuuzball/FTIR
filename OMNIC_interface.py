import win32com.client
import numpy as np
from PIL import ImageGrab

OmApp = win32com.client.Dispatch("OmnicApp.OmnicApp")

def setStageXY(x, y):
	OmApp.ExecuteCommand("stagesetxy {} {}".format(x, y))
	
def getStageXY():
	OmApp.ExecuteCommand("stagegetxy")
	result = OmApp.Get("result array").split(',')
	return map(float, result)

def getMicroscopeImage():
	OmApp.ExecuteCommand("copyvideoimage")
	return ImageGrab.grabclipboard()
	
for (x, y) in [(0,0), (0,1000), (1000,1000), (1000, 0), (0,0)]:
	setStageXY(x,y)
	getMicroscopeImage().show()
x = input("Press RETURN to exit")