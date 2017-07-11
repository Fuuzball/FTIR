import sys, os, random, time
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

imgPath = os.getcwd() + '/scantest/vis_ref.png'

class OmPyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.scanning = False
        self.region_selected = False
        self.scan_points = ScanPoints(parent=self)
        self.initUI()

    def initUI(self):
        self.boxSelector = ScanBoxSelect(0, 0, parent = self) 

        self.btn_toggle_scan = QPushButton('Scan', self)
        self.btn_toggle_scan.setEnabled(False)
        self.btn_toggle_scan.clicked.connect(self.toggle_scanning)

        self.btn_stop_scan = QPushButton('Stop Scanning', self)
        self.btn_stop_scan.setEnabled(False)
        self.btn_toggle_scan.clicked.connect(self.stop_scanning)

        self.status_msg = QLabel('Select region for scanning', self)

        # Fix the size of of box selector
        self.boxSelector.setFixedSize(self.boxSelector.size())

        buttonRow = QHBoxLayout()
        buttonRow.addWidget(self.btn_toggle_scan)
        buttonRow.addWidget(self.btn_stop_scan)

        layout = QVBoxLayout()
        layout.addLayout(buttonRow)
        layout.addWidget(self.boxSelector)
        layout.addWidget(self.status_msg)

        self.setLayout(layout) 
        self.resize(self.boxSelector.size()) 
        self.show()

    def toggle_scanning(self):
        self.scanThread = MockScan(self.boxSelector.ptsXY)
        self.scanThread.start()
        self.scanning = True
        self.update_btns()

    def stop_scanning(self):
        self.scanThread.exit()
        self.scanning = False
        self.update_btns()

    def update_btns(self):
        pass


class ScanBoxSelect(QWidget):

    def __init__(self, x0, y0, a = 3, b = -3, parent = None ):
        super().__init__(parent)
        self.parent = parent
        
        self.a = a
        self.b = b
        self.x0 = x0
        self.y0 = y0

        self.xRes = 5

        self.selecting = False

        self.initUI()

    def initUI(self): 
        #Draw bg image
        self.setWindowTitle('Image test') 
        self.loadRefImg()
        self.boxSelect = Selector(self) 
        self.scanPointVis = PointVis(self.parent.scan_points, self)
        #self.show()

    def loadRefImg(self):
        self.refImg  = QLabel(self)
        pixmap = QPixmap(imgPath)
        self.refImg.setPixmap(pixmap)
        self.rImgW = pixmap.width()
        self.rImgH = pixmap.height()
        self.refImg.resize(self.rImgW, self.rImgH)
        self.resize(self.rImgW, self.rImgH)

    def mousePressEvent(self, event):
        self.selecting = True
        self.curPos = event.pos()
        self.origin = event.pos()

    def mouseMoveEvent(self, event):
        self.curPos = event.pos()
        self.selectPoints()
        self.update()

    def mouseReleaseEvent(self, event):
        self.selecting = False
        self.selectPoints()
        self.parent.update_btns()
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
        for xy in self.getPtSelected():
            self.parent.scan_points.append_point(xy)

    def uv_to_xy(self, u, v):
        x = (u - self.rImgW/2) / self.a + self.x0
        y = (v - self.rImgH/2) / self.b + self.y0
        return x, y

    def xy_to_uv(self, x, y):
        u = (x - self.x0) * self.a + self.rImgW / 2
        v = (y - self.x0) * self.b + self.rImgH / 2
        return u, v


class Selector(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.resize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, e):
        q = QPainter(self)
        if self.parent.selecting:
            q.setPen(QColor(255, 0, 0))
            q.drawRect(
                    QRect(self.parent.origin, self.parent.curPos).normalized()
                    )


class PointVis(QWidget):
    def __init__(self, points, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.points = points
        self.resize(parent.size())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, e):
        q = QPainter(self)
        ptXY = self.points.xy
        ptStat = self.points.status
        for xy, s in zip(ptXY, ptStat):
            uv = self.parent.xy_to_uv(*xy)
            if s == 0:
                q.setPen(QPen(Qt.red, 2))
            if s == -1:
                q.setPen(QPen(Qt.blue, 2))
            if s == 1:
                q.setPen(QPen(Qt.green, 2))
            q.drawPoint(*uv)


class ScanPoints(object):

    def __init__(self, xy = [], status = [], parent = None):
        self.parent = parent
        self.xy = xy
        self.status = status
        self.points_updated()

    def clear_points(self):
        self.xy = []
        self.status = []
        self.points_updated()

    def append_point(self, pt, s=0):
        self.xy.append(pt)
        self.status.append(s)
        self.points_updated()

    def set_status(self, i, s):
        self.status[i] = s
        self.points_updated 

    def set_scanned(self, i):
        self.set_status(1)

    def set_scanning(self, i):
        self.set_status(-1)

    def set_to_scan(self, i):
        self.set_status(0)

    def points_updated(self):
        pass

class MockScan(QThread):

    def __init__(self, points):
        super().__init__()
        self.points = points
        self.i = 0
        self.max_i = len(points)

    def run(self):
        while self.i < self.max_i:
            print(p)
            time.sleep(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = OmPyGUI()
    sys.exit(app.exec_())
