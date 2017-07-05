import win32com.client
import numpy as np
from PIL import ImageGrab
import matplotlib.pylab as plt

om = win32com.client.Dispatch("OmnicApp.OmnicApp")

def Exec(s):
	om.ExecuteCommand(s)

def moveTo(x, y):
	Exec("stagesetxy {} {}".format(x, y))
	
def getXY():
	Exec("stagegetxy")
	result = om.Get("result array").split(',')
	return map(float, result)

def getMicroscopeImage():
	Exec("copyvideoimage")
	return ImageGrab.grabclipboard()
	
def collectBackground():
	Exec("collectbackground")
	
def collectSample():
	Exec("collectsample")
	
def display():
	Exec("display")
	
def newWindow():
	Exec("newwindow")
	
def closeWindow():
	Exec("newwindow")
	
def saveSPA(f):
	Exec("export " + f)
	
def scanAndSave(f):
	newWindow()
	collectSample()
	display()
	saveSPA(f)
	closeWindow()

def listScanWrite(dir, scanList):
	np.save(dir + 'scanPos.npy', np.array(scanList))
	for i, xy in enumerate(scanList):
		fname = str(i) + '.csv'
		x, y = xy
		moveTo(x, y)
		print('scaning at ', (x, y))
		scanAndSave(dir + fname)

def csvToArr(dir):
	scanArr = np.load(dir + 'scanPos.npy')
	arr = np.genfromtxt(dir + '0.csv', delimiter=',')
	waveNumArr = arr[:,0]
	specArr = np.zeros((scanArr.shape[0], arr.shape[0]))

	for i in range(scanArr.shape[0]):
		print(dir + str(i) + '.csv')
		specArr[i] = np.genfromtxt(dir + str(i) + '.csv', delimiter = ',')[:,1]
		
	return waveNumArr, specArr

scanList = [ (0,0), (1000, 0), (1000, 1000), (0, 1000) ]
dir = "I:\\HoiYing\\ompytest\\"



x = input("Press RETURN to exit")
