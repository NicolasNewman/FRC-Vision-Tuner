from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QFileDialog, QCheckBox, QLineEdit, QListWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QEvent
from PyQt5.QtGui import QImage, QPixmap
import sys
import glob
import math
import threading
import cv2
import numpy as np

class OpenCVThread(QThread):
    imageSignal = pyqtSignal(QImage)
    def __init__(self, parent=None, mode="None"):
        QThread.__init__(self)
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

        # HSV Sliders
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

        
        # Solidity sliders
        self.solL = [self.ui.findChild(QSlider, 'sliderSL'), self.ui.findChild(QSlider, 'sliderSL').value()]
        self.solLl = self.ui.findChild(QLabel, 'labelSL')
        self.solLl.setText(str(self.solL[1]))
        self.solL[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.solL, self.solLl))
        
        self.solH = [self.ui.findChild(QSlider, 'sliderSH'), self.ui.findChild(QSlider, 'sliderSH').value()/100.0]
        self.solHl = self.ui.findChild(QLabel, 'labelSH')
        self.solHl.setText(str(self.solH[1]))
        self.solH[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.solH, self.solHl))

        # Extent sliders
        self.extL = [self.ui.findChild(QSlider, 'sliderEL'), self.ui.findChild(QSlider, 'sliderEL').value()]
        self.extLl = self.ui.findChild(QLabel, 'labelEL')
        self.extLl.setText(str(self.extL[1]))
        self.extL[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.extL, self.extLl))
        
        self.extH = [self.ui.findChild(QSlider, 'sliderEH'), self.ui.findChild(QSlider, 'sliderEH').value()/100.0]
        self.extHl = self.ui.findChild(QLabel, 'labelEH')
        self.extHl.setText(str(self.extH[1]))
        self.extH[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.extH, self.extHl))

        # Orientation sliders TODO: remove
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

        # Orientation elements
        self.checkAngle = self.ui.findChild(QCheckBox, 'checkAngle')
        self.checkAngle.stateChanged.connect(self.checkboxChanged)

        self.editAngle = self.ui.findChild(QLineEdit, 'editAngle')
        self.listAngle = self.ui.findChild(QListWidget, 'listAngle')

        self.editAddAngle = self.ui.findChild(QLineEdit, 'editAddAngle')
        self.buttonAddAngle = self.ui.findChild(QPushButton, 'buttonAddAngle')
        self.buttonAddAngle.clicked.connect(self.addAngleClicked)
        self.buttonRemoveAngle = self.ui.findChild(QPushButton, 'buttonRemoveAngle')
        self.buttonRemoveAngle.clicked.connect(self.removeAngleClicked)


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
    
    def checkboxChanged(self):
        self.updated = False
    
    def addAngleClicked(self):
        angleText = self.editAddAngle.text()
        if len(angleText) > 0:
            self.listAngle.addItems([angleText])
        self.updated = False
    
    def removeAngleClicked(self):
        items = self.listAngle.selectedItems()

        for i in items:
            self.listAngle.takeItem(self.listAngle.row(i))
        self.updated = False

    def run(self):
        # self.deleted = False
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
        
        for cnt in contours:
            solidity = self.getSolidity(cnt)
            extent = self.getExtent(cnt)
            aspect = self.getAspectRatio(cnt)
            orientation = self.getOrientation(cnt)
            validAngle = self.validAngle(orientation)
            if self.solL[1] <= solidity <= self.solH[1]:
                if self.extL[1] <= extent <= self.extH[1]:
                    if validAngle:
                        if orientation is not None and (self.oriL[1] <= orientation <= self.oriH[1]): # option to ignore none
                            contourDrawn = False
                            if self.aspect == ">" and aspect > 1:
                                cv2.drawContours(img, cnt, -1, (0, 0, 255), 2) 
                                contourDrawn = True
                            elif self.aspect == "<" and aspect < 1:
                                cv2.drawContours(img, cnt, -1, (0, 0, 255), 2)
                                contourDrawn = True
                            elif self.aspect == "N/A":
                                cv2.drawContours(img, cnt, -1, (0, 0, 255), 2)
                                contourDrawn = True
                            
                            if contourDrawn:
                                if self.checkAngle.isChecked():
                                    self.drawAngles(cnt, img, orientation)

        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # res = cv2.bitwise_and(rgb_frame, rgb_frame, mask= mask)
        convertToQtFormat = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(480, 360)
        
        self.imageSignal.emit(p)  

    def drawAngles(self, cnt, img, orientation):
        M = cv2.moments(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            orientationRad = (orientation+270) * (math.pi / 180)
            length = math.sqrt(w*w + h*h)/3
            cv2.line(img,(cx,cy),(int(cx+length*math.cos(orientationRad)),int(cy+length*math.sin(orientationRad))),(255,0,0),2)
            height, width = img.shape[:2]
            if cx > width/2:
                cv2.putText(img, str(int(orientation)), (cx-int(w/2), cy-int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(img, str(int(orientation)), (cx, cy-int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
    
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
    
    def validAngle(self, orientation):
        try:
            angleList =  [int(self.listAngle.item(i).text()) for i in range(self.listAngle.count())]
            angleTolerance = int(self.editAngle.text())
            if len(angleList) >= 1:
                for angle in angleList:
                    if abs(angle - orientation) <= angleTolerance:
                        return True
                return False
            return True
        except ValueError:
            return True
        except TypeError:
            return True

    def pauseThread(self):
        self.deleted = True
    
    def continueThread(self):
        t = threading.Timer(.5,self.enableThread,args=[])
        t.start()
    
    def enableThread(self):
        self.deleted = False
        self.updated = False
        self.start()
    
    def setMode(self, mode):
        self.mode = mode

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
        self.cvThread = OpenCVThread(self, "Folder")
        self.cvThread.imageSignal.connect(self.setImage)
        pass

    def signal_comboSourceChanged(self, value):
        # if hasattr(self, 'cvThread'):
        #     self.cvThread.pauseThread()
        self.cvThread.pauseThread()
        if value == "Video":
            self.layout_toggle(self.layoutVideo, True)
            self.layout_toggle(self.layoutFolder, False)

            # self.cvThread.imageSignal.connect(self.setImage)
            self.cvThread.setMode("Video")
            self.cvThread.continueThread()
            # self.cvThread.start()
        elif value == "Folder":
            self.layout_toggle(self.layoutVideo, False)
            self.layout_toggle(self.layoutFolder, True)

            # self.cvThread.imageSignal.connect(self.setImage)
            self.cvThread.setMode("Folder")
            self.cvThread.continueThread()
            # self.cvThread.start()
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