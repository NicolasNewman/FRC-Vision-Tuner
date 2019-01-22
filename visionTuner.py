from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QEvent
from PyQt5.QtGui import QImage, QPixmap
import sys
import glob
import cv2

class OpenCVThread(QThread):
    imageSignal = pyqtSignal(QImage)
    def __init__(self, parent=None, mode="None"):
        QThread.__init__(self, parent)
        self.ui = parent
        self.mode = mode
        self.deleted = False

        self.folderMax = self.ui.findChild(QLabel, 'labelFolderMax')
        self.folderSelected = self.ui.findChild(QLabel, 'labelFolderSelected')
        self.folderSelect = self.ui.findChild(QSlider, 'sliderFolderSelect')
    
    def run(self):
        self.deleted = False
        if self.mode == "Video":
            cap = cv2.VideoCapture(0)
            while self.deleted is False:
                ret, bgr_frame = cap.read()
                rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(480, 360)
                self.imageSignal.emit(p)
        elif self.mode == "Folder":
            imgPaths = glob.glob("../img/*.jpg")
            folderSize = len(imgPaths)
            i = 0
            updated = False
            while self.deleted is False:
                if updated is False:
                    bgr_frame = cv2.imread(imgPaths[i])
                    rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                    
                    convertToQtFormat = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(480, 360)
                    self.imageSignal.emit(p)
                    updated = True
    
                    self.folderMax.setText(str(folderSize))
                
                
    
    def __delete__(self):
        self.deleted = True
        self.quit()
        self.wait()

class VisionTuner(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = None
        self.load_ui()
        self.load_cv()
        # self.load_signals()

        self.videoSource = self.ui.findChild(QLabel, 'videoSource')
        
        self.comboSource = self.ui.findChild(QComboBox, 'comboSource')
        self.comboSource.currentTextChanged.connect(self.signal_comboSourceChanged)

        self.layoutVideo = self.ui.findChild(QVBoxLayout, 'layoutVideo')
        self.layout_toggle(self.layoutVideo, False)
        self.layoutFolder = self.ui.findChild(QVBoxLayout, 'layoutFolder')
        self.layout_toggle(self.layoutFolder, False)
        
    def load_ui(self):
        self.ui = loadUi('visionTuner.ui', self)
        self.show()
    
    
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.videoSource.setPixmap(QPixmap.fromImage(image))
    
    def load_cv(self):
        # self.cvThread = OpenCVThread(self, "None")
        pass

    def signal_comboSourceChanged(self, value):
        if hasattr(self, 'cvThread'):
            self.cvThread.__delete__()
        if value == "Video":
            self.layout_toggle(self.layoutVideo, True)
            self.layout_toggle(self.layoutFolder, False)

            self.cvThread = OpenCVThread(self.ui, "Video")
            self.cvThread.imageSignal.connect(self.setImage)
            self.cvThread.start()
        elif value == "Folder":
            self.layout_toggle(self.layoutVideo, False)
            self.layout_toggle(self.layoutFolder, True)

            self.cvThread = OpenCVThread(self.ui, "Folder")
            self.cvThread.imageSignal.connect(self.setImage)
            self.cvThread.start()
        elif value == "None":
            self.layout_toggle(self.layoutVideo, False)
            self.layout_toggle(self.layoutFolder, False)
            
            self.cvThread = OpenCVThread(self.ui, "None")
            
    
    def layout_toggle(self, layout, visible):
        items = (layout.itemAt(i) for i in range(layout.count()))
        for i in items:
            if i.widget() is not None:
                i.widget().setVisible(visible)
            else:
                itemsInner = (i.itemAt(x) for x in range(i.count()))
                for i2 in itemsInner:
                    i2.widget().setVisible(visible)


app = QApplication(sys.argv)
visionTuner = VisionTuner()
sys.exit(app.exec_()) 