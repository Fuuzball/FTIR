import sys, os, random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MouseTracker(QWidget):
    distanceFromCenter = 0
    def __init__(self):
        self.pos = None
        super().__init__()
        self.initUI()
        self.setMouseTracking(True)

    def initUI(self):
        self.setGeometry(200, 200, 1000, 500)
        self.setWindowTitle('Mouse Tracker')
        self.label = QLabel(self)
        self.label.resize(500, 40)
        self.show()
        self.pos = None

    def mouseMoveEvent(self, e):
        distanceFromCenter = round(
                ( (e.y() - 250) **2 + (e.x() - 500)**2 ) ** 0.5
                )
        self.label.setText('Coordinates: (%d : %d)' % (e.x(), e.y()))
        self.pos = e.pos()
        self.update()

    def paintEvent(self, e):
        if self.pos:
            q = QPainter(self)
            q.drawLine(self.pos.x(), self.pos.y(), 500, 250)
            q.drawRect(self.pos.x(), self.pos.y(), 500, 250)


app = QApplication(sys.argv)
ex = MouseTracker()
sys.exit(app.exec_())
