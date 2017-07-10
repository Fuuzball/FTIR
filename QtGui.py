import sys, os, random
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

imgPath = os.getcwd() + '/scantest/vis_ref.png'

class scanBoxSelect(QWidget):

    def __init__(self, x0, y0, a = 3, b = -3 ):
        super().__init__()
        
        self.a = a
        self.b = b
        self.x0 = x0
        self.y0 = y0

        self.xRes = 5

        self.ptsXY = []
        self.ptsStat = []

        self.initUI()

    def initUI(self): 
        #Draw bg image
        self.setWindowTitle('Image test') 
        self.loadRefImg()
        self.boxSelect = selector(self) 
        self.scanPointVis = pointVis([], [], self)
        self.show()

    def loadRefImg(self):
        self.refImg  = QLabel(self)
        pixmap = QPixmap(imgPath)
        self.refImg.setPixmap(pixmap)
        self.rImgW = pixmap.width()
        self.rImgH = pixmap.height()
        self.refImg.resize(self.rImgW, self.rImgH)
        self.resize(self.rImgW, self.rImgH)

    def mousePressEvent(self, event):
        self.boxSelect.selecting = True
        self.boxSelect.origin = event.pos()
        self.origin = event.pos()

    def mouseMoveEvent(self, event):
        self.boxSelect.curPos = event.pos()
        self.curPos = event.pos()
        self.selectPoints()
        self.update()

    def mouseReleaseEvent(self, event):
        self.boxSelect.selecting = False
        self.selectPoints()
        self.update() 

    def getPtSelected(self):
        u0, v0 = self.origin.x(), self.origin.y()
        u1, v1 = self.curPos.x(), self.curPos.y()
        x0, y0 = self.uv_to_xy(u0, v0)
        x1, y1 = self.uv_to_xy(u1, v1)

        x0 = (x0 // self.xRes + 1) * self.xRes
        y0 = (y0 // self.xRes + 1) * self.xRes
        x1 = (x1 // self.xRes + 1) * self.xRes
        y1 = (y1 // self.xRes + 1) * self.xRes
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0

        xList = np.arange(x0, x1, self.xRes)
        yList = np.arange(y0, y1, self.xRes)

        return [(x, y) for y in yList for x in xList]

    def selectPoints(self):
        self.ptsXY = []
        self.ptsStat = []
        for xy in self.getPtSelected():
            self.ptsXY.append(xy)
            self.ptsStat.append(0)

    def uv_to_xy(self, u, v):
        x = (u - self.rImgW/2) / self.a + self.x0
        y = (v - self.rImgH/2) / self.b + self.y0
        return x, y

    def xy_to_uv(self, x, y):
        u = (x - self.x0) * self.a + self.rImgW / 2
        v = (y - self.x0) * self.b + self.rImgH / 2
        return u, v

class selector(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.resize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.selecting = None
        self.origin = None
        self.curPos = None

    def paintEvent(self, e):
        q = QPainter(self)
        if self.selecting:
            q.setPen(QColor(255, 0, 0))
            q.drawRect(
                    QRect(self.origin, self.curPos).normalized()
                    )

class pointVis(QWidget):
    def __init__(self, ptXY, ptStat, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.resize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.ptXY = ptXY
        self.ptStat= ptStat

    def paintEvent(self, e):
        q = QPainter(self)
        ptXY = self.parent.ptsXY
        ptStat = self.parent.ptsStat
        for xy, s in zip(ptXY, ptStat):
            uv = self.parent.xy_to_uv(*xy)
            if s == 0:
                q.setPen(QPen(Qt.red, 2))
            if s == -1:
                q.setPen(QPen(Qt.blue, 2))
            if s == 1:
                q.setPen(QPen(Qt.green, 2))
            q.drawPoint(*uv)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = scanBoxSelect(0, 0)
    sys.exit(app.exec_())
