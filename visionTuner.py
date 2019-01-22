from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QSlider
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QEvent
from PyQt5.QtGui import QImage, QPixmap
import sys
import glob
import cv2
import numpy as np

class OpenCVThread(QThread):
    imageSignal = pyqtSignal(QImage)
    def __init__(self, parent=None, mode="None"):
        QThread.__init__(self, parent)
        self.ui = parent
        self.mode = mode
        self.deleted = False
        self.updated = False
        self.imgIndx = 0

        self.folderMax = self.ui.findChild(QLabel, 'labelFolderMax')
        self.folderSelected = self.ui.findChild(QLabel, 'labelFolderSelected')
        self.folderSelected.setText('1')
        
        self.folderSelect = self.ui.findChild(QSlider, 'sliderFolderSelect')
        self.folderSelect.valueChanged.connect(self.indxSliderChanged)


        self.hh = [self.ui.findChild(QSlider, 'sliderHSV_HH'), 255]
        self.hhl = self.ui.findChild(QLabel, 'labelHSV_HH')
        self.hh[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.hh, self.hhl))
        
        self.hl = [self.ui.findChild(QSlider, 'sliderHSV_HL'), 0]
        self.hll = self.ui.findChild(QLabel, 'labelHSV_HL')
        self.hl[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.hl, self.hll))


        self.sh = [self.ui.findChild(QSlider, 'sliderHSV_SH'), 255]
        self.shl = self.ui.findChild(QLabel, 'labelHSV_SH')
        self.sh[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.sh, self.shl))

        self.sl = [self.ui.findChild(QSlider, 'sliderHSV_SL'), 0]
        self.sll = self.ui.findChild(QLabel, 'labelHSV_SL')
        self.sl[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.sl, self.sll))


        self.vh = [self.ui.findChild(QSlider, 'sliderHSV_VH'), 255]
        self.vhl = self.ui.findChild(QLabel, 'labelHSV_VH')
        self.vh[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.vh, self.vhl))

        self.vl = [self.ui.findChild(QSlider, 'sliderHSV_VL'), 0]
        self.vll = self.ui.findChild(QLabel, 'labelHSV_VL')
        self.vl[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.vl, self.vll))
    
    def indxSliderChanged(self):
        indx = self.folderSelect.value()
        self.imgIndx = indx
        self.folderSelected.setText(str(indx+1))
        self.updated = False
    
    def hsvSliderChanged(self, slider, label):
        sliderVal = slider[0].value()
        slider[1] = sliderVal
        label.setText(str(sliderVal))
        self.updated = False

    def run(self):
        self.deleted = False
        if self.mode == "Video":
            cap = cv2.VideoCapture(0)
            while self.deleted is False:
                ret, bgr_frame = cap.read()

                hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

                highLimitHSV = np.array([self.hh[1], self.sh[1], self.vh[1]])
                lowLimitHSV = np.array([self.hl[1], self.sl[1], self.vl[1]])
                mask = cv2.inRange(hsv_frame, lowLimitHSV, highLimitHSV)

                _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
                
                cv2.drawContours(bgr_frame, contours, -1, (0, 0, 255), 2)   

                rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(480, 360)
                self.imageSignal.emit(p)
        elif self.mode == "Folder":
            imgPaths = glob.glob("../img/*.jpg")
            folderSize = len(imgPaths)
            self.folderMax.setText(str(folderSize))
            self.folderSelect.setMaximum(folderSize-1)
            while self.deleted is False:
                if self.updated is False:
                    bgr_frame = cv2.imread(imgPaths[self.imgIndx])
                    hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

                    highLimitHSV = np.array([self.hh[1], self.sh[1], self.vh[1]])
                    lowLimitHSV = np.array([self.hl[1], self.sl[1], self.vl[1]])
                    mask = cv2.inRange(hsv_frame, lowLimitHSV, highLimitHSV)

                    _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
                    
                    cv2.drawContours(bgr_frame, contours, -1, (0, 0, 255), 2)   
                    
                    rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                    convertToQtFormat = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(480, 360)
                    self.imageSignal.emit(p)
                    self.updated = True
    
                
                
    
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