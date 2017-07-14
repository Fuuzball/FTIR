"""
TODO
-Disable selection once spectra successfully loaded <--- impliment a way of loading data successfully
"""

import sys, os, random, time, csv
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from sklearn import svm

imgPath = os.getcwd() + '/scantest/vis_ref.png'

def getXY():
    return 0, 0



def mock_pic(fname):
    time.sleep(.1)

class PictureTaker(QObject):

    finished = pyqtSignal()
    def __init__(self, fname):
        super().__init__()
        self.fname = fname

    def run(self):
        mock_pic(self.fname)
        self.finished.emit()

class OmPyGUI(QMainWindow):

    # TODO: Load image before loading points
    def __init__(self):
        super().__init__()
        self.scan_status = 'select'
        self.scan_points = ScanPoints(parent=self)
        self.working_dir = '/Users/michael/github_repos/FTIR/scantest2/data'
        self.image_path = os.path.join(self.working_dir, 'vis_ref.png')

        self.x0, self.y0 = getXY()

        self.box_selectable = False
        self.current_scan_i = False
        self.selected_freq = 0
        self.spec_ylim = [0, 1]
        self.spec_xlim = [0, 1000]

        self.total_points_scanned = 0
        
        self.UI_initialized = False
        self.initUI()
        self.update_UI()

    def initUI(self): 
        self.MAXUI_WIDTH = 1200
        self.container = QWidget(self)

        # TODO: Overhaul of the button system
        self.spec_plotter = PlotCanvas(parent=self)
        self.spec_plotter.setFixedHeight(200)

        self.boxSelector = ScanBoxSelect(parent = self) 
        self.boxSelector.setFixedSize(self.boxSelector.size())
        self.spec_vis = SpectralVisualizer(parent = self)
        self.spec_vis.spec_imported.connect(self.spec_imported)
        self.spec_vis.import_spec_data()

        self.btn_take_ref_img = QPushButton('Get Ref. Image', self)
        self.btn_take_ref_img.clicked.connect(self.take_vis_ref_img)

        self.btn_toggle_scan = QPushButton('Scan', self)
        self.btn_toggle_scan.setEnabled(False)
        self.btn_toggle_scan.clicked.connect(self.toggle_scanning)

        self.btn_stop_scan = QPushButton('Stop Scanning', self)
        self.btn_stop_scan.setEnabled(False)
        self.btn_stop_scan.clicked.connect(self.stop_scanning)

        self.btn_select_dir = QPushButton('Set Directory', self)
        self.btn_select_dir.setEnabled(True)
        self.btn_select_dir.clicked.connect(self.select_dir)

        self.btn_import_spec = QPushButton('Import Spectral Data', self)
        self.btn_import_spec.setEnabled(True)
        self.btn_import_spec.clicked.connect(self.spec_vis.import_spec_data)

        self.btn_toggle_spec_mode = QPushButton('Toggle spec. mode', self)
        self.btn_toggle_spec_mode.clicked.connect(self.toggle_spec_mode)

        self.btn_predict_roi = QPushButton('Predict Region of Interest', self)
        self.btn_predict_roi.clicked.connect(self.predict_roi)

        self.statusBar().showMessage('Ready')

        self.resize_spec_vis()

        spec_cont = DenseContainer()
        spec_cont_layout = QVBoxLayout()
        spec_cont_layout.addStretch(1)
        spec_cont_layout.addWidget(self.spec_vis)
        spec_cont_layout.addStretch(1)
        spec_cont_layout.setContentsMargins(0, 0, 0, 0)
        spec_cont.setLayout(spec_cont_layout)
        spec_cont.setFixedHeight(self.boxSelector.size().height())

        buttonRow = QHBoxLayout()
        buttonRow.addWidget(self.btn_take_ref_img)
        buttonRow.addWidget(self.btn_select_dir)
        buttonRow.addWidget(self.btn_toggle_scan)
        buttonRow.addWidget(self.btn_stop_scan)
        buttonRow.addWidget(self.btn_import_spec)
        buttonRow.addWidget(self.btn_toggle_spec_mode) 
        buttonRow.addWidget(self.btn_predict_roi)
        display_row = QHBoxLayout()
        display_row.addWidget(self.boxSelector)
        #display_row.addWidget(self.spec_vis)
        display_row.addWidget(spec_cont)


        layout = QVBoxLayout()
        layout.addLayout(buttonRow)
        layout.addLayout(display_row)
        layout.addWidget(self.spec_plotter)

        self.container.setLayout(layout) 
        
        self.setCentralWidget(self.container)

        self.UI_initialized = True
        self.update_UI()
        self.show()

    def spec_imported(self):
        self.total_points_scanned = len(self.spec_vis.spectra)
        self.resize_spec_vis()
        self.updated_spec_pix_selection()
        self.spec_vis.update()

    def resize_spec_vis(self):
        selector_height = self.boxSelector.size().height()
        spec_aspect_ratio = self.spec_vis.aspect_ratio
        spec_width = spec_aspect_ratio * selector_height
        if spec_width + self.boxSelector.size().width() > self.MAXUI_WIDTH:
            spec_width = self.MAXUI_WIDTH - self.boxSelector.size().width()
            spec_height = spec_width / spec_aspect_ratio
            self.spec_vis.setFixedSize(spec_width, spec_height)
        else:
            self.spec_vis.setFixedSize(spec_aspect_ratio * selector_height, selector_height)

    def take_vis_ref_img(self):
        self.picture_thread = QThread()
        self.picture_taker = PictureTaker(self.image_path)
        self.picture_taker.moveToThread(self.picture_thread)

        self.picture_thread.started.connect(self.picture_taker.run)
        self.picture_taker.finished.connect(self.finished_loading_pic)

        self.picture_thread.start()

    def finished_loading_pic(self):
        self.boxSelector.load_ref_img()

    def start_scanning(self): 
        self.scan_thread = QThread()
        print(self.total_points_scanned)
        self.scan_runner = ScanRunner(self.scan_points, self.working_dir, self.total_points_scanned)
        self.scan_runner.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scan_runner.run)

        self.scan_runner.begin_scan_pt.connect(self.begin_scanning_point)
        self.scan_runner.done_scan_pt.connect(self.done_scanning_point)
        self.scan_runner.finished.connect(self.finished_scanning)

        self.scan_thread.start()

        self.update_UI()

    def begin_scanning_point(self, i):
        self.current_scan_i = i
        self.update_UI()

    def done_scanning_point(self, i):
        self.scan_points.set_scanned(i)

    def toggle_scanning(self): 
        print('toggle scanning-----')
        print('Sender: {}'.format(self.sender().text()))
        print(self.scan_status)
        print('-----')
        if self.scan_status == 'ready':
            self.scan_status = 'scanning'
            self.start_scanning()

        elif self.scan_status == 'scanning':
            self.scan_status = 'paused'
            self.scan_runner.is_scanning = False
            #self.update_UI()

        elif self.scan_status == 'paused':
            self.scan_status = 'scanning'
            self.start_scanning()

    def update_UI(self):
        # TODO Fix the statuses
        if self.UI_initialized:
            if self.scan_status == 'select':
                self.btn_toggle_scan.setEnabled(False) 
                self.btn_stop_scan.setEnabled(False)
                self.btn_toggle_scan.setText('Start Scan')
                if self.working_dir:
                    self.statusBar().showMessage('Select region for scanning')
                    self.box_selectable = True
                else:
                    self.statusBar().showMessage('Select directory to store files')
                    self.box_selectable = False
            elif self.scan_status == 'ready': 
                self.btn_toggle_scan.setEnabled(True) 
                self.btn_stop_scan.setEnabled(False) 
                self.btn_toggle_scan.setText('Start Scan')
                self.statusBar().showMessage('Ready for scanning')
                self.box_selectable = True
            elif self.scan_status == 'scanning':
                self.btn_toggle_scan.setEnabled(True)
                self.btn_stop_scan.setEnabled(True)
                self.btn_toggle_scan.setText('Pause')
                if self.current_scan_i:
                    print(self.current_scan_i)
                    print(self.scan_points.xy)
                    x, y = self.scan_points.xy[self.current_scan_i]
                    self.statusBar().showMessage('Scanning ({}, {})'.format(x, y))
                else:
                    self.statusBar().showMessage('Scanning...')
                self.box_selectable = False
            elif self.scan_status == 'paused':
                print('status paused')
                self.btn_toggle_scan.setEnabled(True)
                self.btn_stop_scan.setEnabled(True) 
                self.btn_toggle_scan.setText('Resume Scan')
                self.statusBar().showMessage('Scanning Paused')
                self.box_selectable = False
            elif self.scan_status == 'finished':
                print('status finished')
                self.btn_toggle_scan.setEnabled(False)
                self.btn_stop_scan.setEnabled(False) 
                self.statusBar().showMessage('Finished Scaning')
                self.box_selectable = False
            elif self.scan_status == 'stopping':
                self.btn_toggle_scan.setEnabled(False)
                self.btn_stop_scan.setEnabled(False) 
                self.statusBar().showMessage('Stopping Scan')
                self.box_selectable = False
            
    def stop_scanning(self):
        print('stop scanning-----')
        print(self.sender())
        if self.scan_runner.is_scanning:
            self.scan_runner.is_scanning = False
            self.scan_thread.exit()
            #self.scan_points.clear_points()
            self.scan_status = 'stopping'
        else:
            self.scan_status = 'select'
        self.update_UI()

    def finished_scanning(self):
        print('finished scan')
        if self.scan_status == 'stopping':
            self.scan_status = 'select'
            self.scan_points.clear_points()
        else: 
            if 0 in self.scan_points.status:
                self.scan_status = 'paused'
                self.scan_thread.exit()
            else:
                self.scan_status = 'finished'
                self.scan_thread.exit()
        self.spec_vis.import_spec_data()
        self.update_UI()

    def select_dir(self):
        self.working_dir = QFileDialog.getExistingDirectory(self, 'Select working directory') 
        self.update_UI()

    def updated_spec_pix_selection(self):
        # TODO Move selected_index to main window
        i = self.spec_vis.selected_index
        data = self.spec_vis.spectra[i].T
        plt.plot(*data)
        self.spec_plotter.data = data
        self.spec_plotter.replot()

    def toggle_spec_mode(self):
        if self.spec_vis.mode == 'view':
            self.spec_vis.mode = 'select'
        elif self.spec_vis.mode == 'select':
            self.spec_vis.mode = 'view'
        self.spec_vis.update()

    def predict_roi(self):
        acc_i = self.spec_vis.accepted_indices
        rej_i = self.spec_vis.rejected_indices
        spec = self.spec_vis.spectra

        X = []
        y = []
        for i in acc_i:
            X.append(spec[i][:,1])
            y.append(1)
        for i in rej_i:
            X.append(spec[i][:,1])
            y.append(0)
        X = np.vstack(X) 
        y = np.vstack(y)

        clf = svm.SVC(kernel = 'linear')
        clf.fit(X, y)

        spec_arr = np.array(spec)[:, :, 1]
        prediction = clf.predict(spec_arr)
        new_to_scan = []
        for idx, pred in enumerate(prediction):
            if pred == 1:
                self.spec_vis.predicted_indices.add(idx)
                new_to_scan.append(self.scan_points.xy[idx])
        self.spec_vis.accepted_indices = set([])
        self.spec_vis.rejected_indices = set([])
        self.scan_points.set_points_to_scan(new_to_scan)
        self.scan_status = 'ready'
        self.update_UI()
        



class ScanBoxSelect(QWidget):

    def __init__(self, a = 3, b = -3, parent = None ):
        super().__init__(parent)
        self.parent = parent
        
        self.a = a
        self.b = b
        self.x0 = parent.x0
        self.y0 = parent.y0

        self.xRes = 5

        self.selecting = False

        self.initUI()

    def initUI(self): 
        self.refImg  = QLabel(self)
        self.load_ref_img_init()
        try:
            self.load_ref_img()
        except:
            pass
        self.boxSelect = Selector(self) 
        self.scanPointVis = PointVis(self.parent.scan_points, self)
        self.w = 640
        self.h = 480
        self.resize(self.w, self.h)

    def load_ref_img_init(self):
        pixmap = QPixmap(self.parent.image_path)
        #self.refImg.setPixmap(pixmap)
        self.w = pixmap.width()
        self.h = pixmap.height()
        #self.refImg.resize(self.w, self.h)
        self.resize(self.w, self.h)
        self.update()

    def load_ref_img(self):
        pixmap = QPixmap(self.parent.image_path)
        self.refImg.setPixmap(pixmap)
        self.w = pixmap.width()
        self.h = pixmap.height()
        self.refImg.resize(self.w, self.h)
        self.resize(self.w, self.h)
        self.update()

    def mousePressEvent(self, event):
        if self.parent.box_selectable:
            self.parent.scan_points.clear_points()
            self.selecting = True
            self.curPos = event.pos()
            self.origin = event.pos()

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.curPos = event.pos()
            self.parent.scan_points.set_points_to_scan(self.getPtSelected())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.selecting:
            self.selecting = False
            self.parent.scan_points.set_points_to_scan(self.getPtSelected())
            if self.parent.scan_points.xy:
                self.parent.scan_status = 'ready'
            else:
                self.parent.scan_status = 'select' 
            self.parent.update_UI()
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

    def uv_to_xy(self, u, v):
        x = (u - self.w/2) / self.a + self.x0
        y = (v - self.h/2) / self.b + self.y0
        return x, y

    def xy_to_uv(self, x, y):
        u = (x - self.x0) * self.a + self.w / 2
        v = (y - self.x0) * self.b + self.h / 2
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
            q.setPen(Qt.NoPen)
            if s == 0:
                q.setBrush(QBrush(Qt.blue))
            if s == -1:
                q.setBrush(QBrush(Qt.black))
            if s == 1:
                q.setBrush(QBrush(Qt.green))
            #q.drawPoint(*uv)
            r = self.parent.xRes * 0.6
            q.drawEllipse(QPoint(*uv), r, r)


class ScanPoints(object):

    def __init__(self, xy = [], status = [], parent = None):
        self.parent = parent
        self.xy = xy
        self.status = status
        #self.points_updated()

    def clear_points(self):
        self.xy = []
        self.status = []
        self.points_updated()

    def set_points_to_scan(self, points):
        self.xy = points
        self.status = [0 for p in points]
        self.points_updated()

    def set_points_scanned(self, points):
        self.xy = points
        self.status = [1 for p in points]
        self.points_updated()

    def append_point(self, pt, s=0):
        self.xy.append(pt)
        self.status.append(s)
        self.points_updated()

    def set_status(self, i, s):
        self.status[i] = s
        self.points_updated()

    def set_scanned(self, i):
        self.set_status(i, 1)

    def set_scanning(self, i):
        self.set_status(i, -1)

    def set_to_scan(self, i):
        self.set_status(i, 0)

    def points_updated(self):
        self.max_idx = len(self.xy)
        self.parent.update_UI()
        self.parent.update()


class ScanRunner(QObject):

    finished = pyqtSignal()
    begin_scan_pt = pyqtSignal(int)
    done_scan_pt = pyqtSignal(int)

    def __init__(self, points, dir, prev_last):
        super().__init__()
        self.points = points
        self.dir = dir
        self.is_scanning = True
        self.prev_last = prev_last

    def run(self):
        sample_fname = os.path.join(self.dir, 'sample.csv')
        sample_arr = np.genfromtxt(sample_fname, delimiter = ',')
        sample_freq = sample_arr[:,0]
        scan_csv_fname = os.path.join(self.dir, 'scan_points.csv')
        while self.is_scanning:
            if 0 in self.points.status:
                i = self.points.status.index(0)
                self.points.set_scanning(i)
                xy = self.points.xy[i]
                self.begin_scan_pt.emit(i)

                fname = os.path.join(self.dir, str(self.prev_last + i) + '.csv')
                mock_scan(xy, fname, sample_arr)
                line = [xy[0], xy[1], time.time()]
                with open(scan_csv_fname, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(line)

                self.done_scan_pt.emit(i)
            else:
                break
        self.finished.emit()

class SpectralVisualizer(QWidget):

    spec_imported = pyqtSignal()
    def __init__(self, parent = None):
        #Assuming that points are spaced isotropically (x-, y- direction) in a rect. lattice
        super().__init__(parent)
        self.parent = parent
        self.working_dir = self.parent.working_dir
        self.scanned_csv_fname = os.path.join(self.working_dir, 'scan_points.csv')
        self.aspect_ratio = 1.5
        self.selected_index = 0
        self.accepted_indices = set([])
        self.rejected_indices = set([])
        self.predicted_indices = set([])
        self.mode = 'view'

        #self.grid = None
        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid)
        

    def import_spec_data(self):
        try: 
            self.scanned_points = np.loadtxt(
                    open(self.scanned_csv_fname, 'rb'), delimiter=','
                    )
            self.parent.scan_points.set_points_scanned(self.scanned_points[:,:2])
            self.import_spectra()
            self.make_spec_vis_arr()
            self.aspect_ratio = self.get_aspect_ratio()
            self.selected_index = 0
            self.spec_imported.emit()
        except FileNotFoundError:
            print('Did not successfully load spectral data')

    def import_spectra(self):
        self.spectra = []
        for i, _ in enumerate(self.scanned_points):
            fname = os.path.join(self.working_dir, str(i) + '.csv')
            self.spectra.append(
                    np.loadtxt(
                        open(fname, 'rb'), delimiter=','
                        )
                    )

    def get_aspect_ratio(self):
        w = self.index_array.max(0)[0] + 1
        h = self.index_array.max(0)[1] + 1
        return w / h

    def make_spec_vis_arr(self):
        #TODO this is really messy, fixit
        unique_x = np.unique(self.scanned_points[:,0])
        unique_y = -np.unique(-self.scanned_points[:,1])
        self.index_array = np.zeros_like(self.scanned_points[:,:2])
        for i, x in enumerate(unique_x):
            self.index_array[self.scanned_points[:,0] == x, 0] = i
        for j, y in enumerate(unique_y):
            self.index_array[self.scanned_points[:,1] == y, 1] = j

        self.spec_pix = []

        idx_arr = self.index_array
        self.unique_enum_index_arr = []
        for pair in {tuple(row) for row in idx_arr}: 
            self.unique_enum_index_arr.append(
                    (np.argwhere(np.all(idx_arr == pair, 1))[-1][0], pair)
                    )




        #for idx, ij in enumerate(self.index_array):
        for idx, ij in self.unique_enum_index_arr:
            pix = SpecSquare(idx, parent=self)
            self.spec_pix.append(pix)
            j, i = ij
            self.grid.addWidget(pix, i, j)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def paintEvent(self, e):
        q = QPainter(self)
        q.setBrush(QBrush(Qt.gray))
        q.drawRect(self.rect())
        frame_w, frame_h = self.size().width(), self.size().height()

    def get_index_from_mouse(self, pos):
        i_max, j_max = self.index_array.max(0) + 1
        w, h = self.size().width(), self.size().height()
        x, y = pos.x(), pos.y()
        i = int(x / w * i_max)
        j = int(y / h * j_max)
        try:
            idx = np.nonzero(np.all(self.index_array == [i, j], axis=1))[0][-1]
            #TODO impliment multiple scans
            print(idx)
            return idx
        except IndexError:
            print('missing pix')
            return None

    def mousePressEvent(self, e):
        self.mouse_down_event(e)

    def mouseMoveEvent(self, e):
        self.mouse_down_event(e)

    def mouse_down_event(self, e):
        idx = self.get_index_from_mouse(e.pos())
        if self.mode == 'view':
            self.change_selection(idx)
        elif self.mode == 'select':
            if self.predicted_indices:
                self.predicted_indices = set([])
            if e.buttons() == Qt.LeftButton:
                self.rejected_indices.discard(idx)
                self.accepted_indices.add(idx)
            elif e.buttons() == Qt.RightButton:
                self.accepted_indices.discard(idx)
                self.rejected_indices.add(idx)
            print('acc', self.accepted_indices)
            print('rej', self.rejected_indices)
            print('pred', self.predicted_indices)
            self.update()

    def change_selection(self, idx):
        if (idx != None) and (idx != self.selected_index):
            self.selected_index = idx
            self.parent.updated_spec_pix_selection()
            self.update()



class SpecSquare(QWidget):

    def __init__(self, index, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.index = index
        self.selected = False
        self.setMouseTracking(True)
        #self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, e):
        spec_data = self.parent.spectra[self.index]
        freq = self.parent.parent.selected_freq
        idx = (np.abs(spec_data[:,0] - freq)).argmin()
        val = spec_data[idx, 1]
        print(self.index, val)
        ymin, ymax = self.parent.parent.spec_ylim
        color_val = 255 * (val - ymin) / (ymax - ymin) 
    
        q = QPainter(self)
        #if (self.index == self.parent.selected_index) and (self.parent.mode == 'view'):
        #    q.setPen(QPen(Qt.blue, 5))
        #elif self.parent.mode == 'select':
        if self.index in self.parent.predicted_indices:
            q.setPen(QPen(Qt.blue, 5))
        elif self.index in self.parent.accepted_indices:
            q.setPen(QPen(Qt.green, 5))
        elif self.index in self.parent.rejected_indices:
            q.setPen(QPen(Qt.red, 5))
        else:
            q.setPen(Qt.NoPen)
        q.setBrush(QColor(color_val, color_val, color_val))
        q.drawRect(self.rect())
        frame_w, frame_h = self.size().width(), self.size().height()


class DenseContainer(QWidget):
    
    def paintEvent(self, e):
        q = QPainter(self)
        q.setBrush(QBrush(Qt.Dense6Pattern))
        q.drawRect(self.rect())
        

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=30, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)

        fig.tight_layout()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.parent = parent
        print(self.parent)

        self.plot_init()
        self.mpl_connect('button_press_event', self.mouse_down)
        #self.replot()
    
    def plot_init(self):
        #self.ax = self.figure.add_subplot(111)
        self.spec_plot = None
        #self.spec_plot, = self.ax.plot(self.data, 'r-', linewidth=1)
        #self.cursor_line = self.ax.axvline(x=self.cursor_x, color='b', linewidth=.5)
        self.cursor_line = None
        self.draw()

    def replot(self):
        if self.spec_plot:
            self.spec_plot.remove()
        self.spec_plot, = self.ax.plot(*self.data, 'r-', linewidth=1)
        xmin, xmax = self.data[0].min(), self.data[0].max()
        self.parent.spec_xlim = [xmin, xmax]
        self.ax.set_xlim(self.parent.spec_xlim)
        self.ax.set_ylim(self.parent.spec_ylim)
        if self.parent.selected_freq < xmin:
            self.parent.selected_freq = xmin
        elif self.parent.selected_freq > xmax:
            self.parent.selected_freq = xmax
        self.draw_cursor_line()

    def mouse_down(self, e):
        if e.xdata:
            self.parent.selected_freq = e.xdata
            self.draw_cursor_line()
            self.parent.update()

    def draw_cursor_line(self):
        if self.cursor_line:
            self.cursor_line.remove()
        self.cursor_line = self.ax.axvline(x=self.parent.selected_freq, color='b', linewidth=.5)
        self.draw()


def mock_scan(xy, fname, sample_arr):
    #Make fake data
    freq = sample_arr[:,0]
    rand_arr = (np.random.rand(sample_arr.shape[0]))
    sample_arr[:,1] = np.convolve(rand_arr, np.ones(20), mode = 'same')/ 20
    #time.sleep(.1)

    np.savetxt(fname, sample_arr, delimiter = ',')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = OmPyGUI()
    sys.exit(app.exec_())
