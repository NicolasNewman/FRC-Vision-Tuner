from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QFileDialog
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
        self.directory = "img/"
        self.aspect = "N/A"

        self.folderMax = self.ui.findChild(QLabel, 'labelFolderMax')
        self.folderSelected = self.ui.findChild(QLabel, 'labelFolderSelected')
        self.folderSelected.setText('1')
        
        self.folderSelect = self.ui.findChild(QSlider, 'sliderFolderSelect')
        self.folderSelect.valueChanged.connect(self.indxSliderChanged)

        self.folderButton = self.ui.findChild(QPushButton, 'buttonFolderSelect')
        self.folderButton.clicked.connect(self.selectFolder)

        self.folderLabel = self.ui.findChild(QLabel, 'labelFolderDir')

        self.hh = [self.ui.findChild(QSlider, 'sliderHSV_HH'), self.ui.findChild(QSlider, 'sliderHSV_HH').value()]
        self.hhl = self.ui.findChild(QLabel, 'labelHSV_HH')
        self.hhl.setText(str(self.hh[1]))
        self.hh[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.hh, self.hhl))
        
        self.hl = [self.ui.findChild(QSlider, 'sliderHSV_HL'), self.ui.findChild(QSlider, 'sliderHSV_HL').value()]
        self.hll = self.ui.findChild(QLabel, 'labelHSV_HL')
        self.hll.setText(str(self.hl[1]))
        self.hl[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.hl, self.hll))


        self.sh = [self.ui.findChild(QSlider, 'sliderHSV_SH'), self.ui.findChild(QSlider, 'sliderHSV_SH').value()]
        self.shl = self.ui.findChild(QLabel, 'labelHSV_SH')
        self.shl.setText(str(self.sh[1]))
        self.sh[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.sh, self.shl))

        self.sl = [self.ui.findChild(QSlider, 'sliderHSV_SL'), self.ui.findChild(QSlider, 'sliderHSV_SL').value()]
        self.sll = self.ui.findChild(QLabel, 'labelHSV_SL')
        self.sll.setText(str(self.sl[1]))
        self.sl[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.sl, self.sll))


        self.vh = [self.ui.findChild(QSlider, 'sliderHSV_VH'), self.ui.findChild(QSlider, 'sliderHSV_VH').value()]
        self.vhl = self.ui.findChild(QLabel, 'labelHSV_VH')
        self.vhl.setText(str(self.vh[1]))
        self.vh[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.vh, self.vhl))

        self.vl = [self.ui.findChild(QSlider, 'sliderHSV_VL'), self.ui.findChild(QSlider, 'sliderHSV_VL').value()]
        self.vll = self.ui.findChild(QLabel, 'labelHSV_VL')
        self.vll.setText(str(self.vl[1]))
        self.vl[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.vl, self.vll))

        
        self.solL = [self.ui.findChild(QSlider, 'sliderSL'), self.ui.findChild(QSlider, 'sliderSL').value()]
        self.solLl = self.ui.findChild(QLabel, 'labelSL')
        self.solLl.setText(str(self.solL[1]))
        self.solL[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.solL, self.solLl))
        
        self.solH = [self.ui.findChild(QSlider, 'sliderSH'), self.ui.findChild(QSlider, 'sliderSH').value()/100.0]
        self.solHl = self.ui.findChild(QLabel, 'labelSH')
        self.solHl.setText(str(self.solH[1]))
        self.solH[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.solH, self.solHl))
    
        self.extL = [self.ui.findChild(QSlider, 'sliderEL'), self.ui.findChild(QSlider, 'sliderEL').value()]
        self.extLl = self.ui.findChild(QLabel, 'labelEL')
        self.extLl.setText(str(self.extL[1]))
        self.extL[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.extL, self.extLl))
        
        self.extH = [self.ui.findChild(QSlider, 'sliderEH'), self.ui.findChild(QSlider, 'sliderEH').value()/100.0]
        self.extHl = self.ui.findChild(QLabel, 'labelEH')
        self.extHl.setText(str(self.extH[1]))
        self.extH[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.extH, self.extHl))

        self.oriL = [self.ui.findChild(QSlider, 'sliderOL'), self.ui.findChild(QSlider, 'sliderOL').value()]
        self.oriLl = self.ui.findChild(QLabel, 'labelOL')
        self.oriLl.setText(str(self.oriL[1]))
        self.oriL[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.oriL, self.oriLl))
        
        self.oriH = [self.ui.findChild(QSlider, 'sliderOH'), self.ui.findChild(QSlider, 'sliderOH').value()]
        self.oriHl = self.ui.findChild(QLabel, 'labelOH')
        self.oriHl.setText(str(self.oriH[1]))
        self.oriH[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.oriH, self.oriHl))
        
        self.comboAspect = self.ui.findChild(QComboBox, 'comboAspect')
        self.comboAspect.currentTextChanged.connect(self.aspectComboChanged)

    def selectFolder(self):
        self.directory = str(QFileDialog.getExistingDirectory(None, "Select Image Directory")) + "/"
        self.folderLabel.setText(self.directory)

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
    
    def ratioSliderChanged(self, slider, label):
        sliderVal = slider[0].value() / 100.0
        slider[1] = sliderVal
        label.setText(str(sliderVal))
        self.updated = False

    def aspectComboChanged(self):
        self.aspect = self.comboAspect.currentText()
        self.updated = False

    def run(self):
        self.deleted = False
        if self.mode == "Video":
            cap = cv2.VideoCapture(0)
            while self.deleted is False:
                ret, bgr_frame = cap.read()
                self.processImage(bgr_frame)

        elif self.mode == "Folder":
            imgPaths = glob.glob(self.directory + "*.jpg")
            imgPaths.extend(glob.glob(self.directory + "*.png"))
            folderSize = len(imgPaths)
            self.folderMax.setText(str(folderSize))
            self.folderSelect.setMaximum(folderSize-1)
            while self.deleted is False:
                if self.updated is False:
                    bgr_frame = cv2.imread(imgPaths[self.imgIndx])
                    self.processImage(bgr_frame)
                    self.updated = True
    
    def processImage(self, img):
        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        highLimitHSV = np.array([self.hh[1], self.sh[1], self.vh[1]])
        lowLimitHSV = np.array([self.hl[1], self.sl[1], self.vl[1]])
        mask = cv2.inRange(hsv_frame, lowLimitHSV, highLimitHSV)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        
        # cv2.drawContours(img, contours, -1, (0, 0, 255), 2)  
        print("-----------") 
        for cnt in contours:
            solidity = self.getSolidity(cnt)
            extent = self.getExtent(cnt)
            aspect = self.getAspectRatio(cnt)
            orientation = self.getOrientation(cnt)
            # print("{} <= {} <= {}".format(self.solL[1], solidity, self.solH[1]))
            if self.solL[1] <= solidity <= self.solH[1]:
                if self.extL[1] <= extent <= self.extH[1]:
                    if orientation is None or (self.oriL[1] <= orientation <= self.oriH[1]): # option to ignore none
                        if self.aspect == ">" and aspect > 1:
                            print(">")
                            cv2.drawContours(img, cnt, -1, (0, 255, 0), 2) 
                        elif self.aspect == "<" and aspect < 1:
                            print("<")
                            cv2.drawContours(img, cnt, -1, (0, 255, 0), 2)
                        elif self.aspect == "N/A":
                            cv2.drawContours(img, cnt, -1, (0, 255, 0), 2)

                    # # orientation
                    # if (len(cnt) >= 5):
                    #     (x,y),(MA,ma),angle = cv2.fitEllipse(cnt)
                    #     print(angle)
                    
                    # # aspect ratio
                    # x,y,w,h = cv2.boundingRect(cnt)
                    # if h != 0:
                    #     aspect_ratio = float(w)/h
                    #     print(aspect_ratio)    
                # print("pass")
        
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = cv2.bitwise_and(rgb_frame, rgb_frame, mask= mask)
        convertToQtFormat = QImage(res, res.shape[1], res.shape[0], res.shape[1] * 3, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(480, 360)
        
        self.imageSignal.emit(p)             
    
    def getSolidity(self, cnt):
        area = cv2.contourArea(cnt)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area != 0:
           return float(area)/hull_area
        return 0
    
    def getExtent(self, cnt):
        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        rect_area = w*h
        if rect_area != 0:
            return float(area)/rect_area
        return 0

    def getAspectRatio(self, cnt):
        x,y,w,h = cv2.boundingRect(cnt)
        if h != 0:
            return float(w)/h
        return None
    
    def getOrientation(self, cnt):
        if (len(cnt) >= 5):
            (x,y),(MA,ma),angle = cv2.fitEllipse(cnt)
            return angle
        return None

    def delete(self):
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
        self.cvThread = OpenCVThread(self, "None")
        pass

    def signal_comboSourceChanged(self, value):
        if hasattr(self, 'cvThread'):
            self.cvThread.delete()
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