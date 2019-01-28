import numpy as np
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QFileDialog, QCheckBox, QLineEdit, QListWidget, QTabWidget, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QEvent
from PyQt5.QtGui import QImage, QPixmap
import sys
import glob
import urllib
import math
import threading
import cv2

class OpenCVThread(QThread):
    imageSignal = pyqtSignal(QImage)
    def __init__(self, parent=None, mode="None"):
        QThread.__init__(self)
        self.ui = parent
        self.mode = mode
        # Used to stop the main loop
        self.deleted = False
        # Used when in Folder mode to signal that a change was made to the image
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

        # Filtering Mode
        self.comboFilterMode = self.ui.findChild(QComboBox, 'comboFilterMode')

        # Channel Sliders
        self.channelB = [self.ui.findChild(QSlider, 'sliderChannelB'), self.ui.findChild(QSlider, 'sliderChannelB').value()]
        self.channelBL = self.ui.findChild(QLabel, 'labelChannelB')
        self.channelB[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.channelB, self.channelBL))
        
        self.channelR = [self.ui.findChild(QSlider, 'sliderChannelR'), self.ui.findChild(QSlider, 'sliderChannelR').value()]
        self.channelRL = self.ui.findChild(QLabel, 'labelChannelR')
        self.channelR[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.channelR, self.channelRL))

        self.channelOtsu = [self.ui.findChild(QSlider, 'sliderChannelOtsu'), self.ui.findChild(QSlider, 'sliderChannelOtsu').value()]
        self.channelOtsuL = self.ui.findChild(QLabel, 'labelChannelOtsu')
        self.channelOtsu[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.channelOtsu, self.channelOtsuL))
        
        # Contour Info
        self.contourInfoCheck = self.ui.findChild(QCheckBox, 'checkContourInfo')
        self.contourInfoCheck.stateChanged.connect(self.checkboxChanged)
        self.contourInfoTab = self.ui.findChild(QTabWidget, 'tabWidgetContourInfo')

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

        # Side sliders
        self.sideMin = [self.ui.findChild(QSlider, 'sliderSideMin'), self.ui.findChild(QSlider, 'sliderSideMin').value()]
        self.sideMinl = self.ui.findChild(QLabel, 'labelSideMin')
        self.sideMinl.setText(str(self.sideMin[1]))
        self.sideMin[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.sideMin, self.sideMinl))
        
        self.sideMax = [self.ui.findChild(QSlider, 'sliderSideMax'), self.ui.findChild(QSlider, 'sliderSideMax').value()]
        self.sideMaxl = self.ui.findChild(QLabel, 'labelSideMax')
        self.sideMaxl.setText(str(self.sideMax[1]))
        self.sideMax[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.sideMax, self.sideMaxl))

        self.sideApprox = [self.ui.findChild(QSlider, 'sliderSideApprox'), self.ui.findChild(QSlider, 'sliderSideApprox').value() / 100.0]
        self.sideApproxl = self.ui.findChild(QLabel, 'labelSideApprox')
        self.sideApproxl.setText(str(self.sideApprox[1]))
        self.sideApprox[0].valueChanged.connect(lambda: self.ratioSliderChanged(self.sideApprox, self.sideApproxl))
        
        # Aspect ratio
        self.comboAspect = self.ui.findChild(QComboBox, 'comboAspect')
        self.comboAspect.currentTextChanged.connect(self.aspectComboChanged)

        # Morphological elements

        self.morphKernel = [self.ui.findChild(QSlider, 'sliderMorphKernel'), self.ui.findChild(QSlider, 'sliderMorphKernel').value()]
        self.morphKernell = self.ui.findChild(QLabel, 'labelMorphKernel')
        self.morphKernel[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.morphKernel, self.morphKernell))
        
        self.morphIteration = [self.ui.findChild(QSlider, 'sliderMorphIteration'), self.ui.findChild(QSlider, 'sliderMorphIteration').value()]
        self.morphIterationl = self.ui.findChild(QLabel, 'labelMorphIteration')
        self.morphIteration[0].valueChanged.connect(lambda: self.hsvSliderChanged(self.morphIteration, self.morphIterationl))

        # Orientation elements
        self.checkAngle = self.ui.findChild(QCheckBox, 'checkAngle')
        self.checkAngle.stateChanged.connect(self.checkboxChanged)

        self.editAngle = self.ui.findChild(QLineEdit, 'editAngle')
        self.editAngle.returnPressed.connect(self.signalUpdate)
        self.listAngle = self.ui.findChild(QListWidget, 'listAngle')

        self.editAddAngle = self.ui.findChild(QLineEdit, 'editAddAngle')

        self.buttonAddAngle = self.ui.findChild(QPushButton, 'buttonAddAngle')
        self.buttonAddAngle.clicked.connect(self.addAngleClicked)
        self.buttonRemoveAngle = self.ui.findChild(QPushButton, 'buttonRemoveAngle')
        self.buttonRemoveAngle.clicked.connect(self.removeAngleClicked)

    # Used to signal an update from a connecter
    def signalUpdate(self):
        self.updated = False

    # Called when the select folder button is clicked
    def selectFolder(self):
        self.directory = str(QFileDialog.getExistingDirectory(None, "Select Image Directory")) + "/"
        self.folderLabel.setText(self.directory)

    # Called when the slider for selecting an image is changed
    def indxSliderChanged(self):
        indx = self.folderSelect.value()
        self.imgIndx = indx
        self.folderSelected.setText(str(indx+1))
        self.updated = False
    
    # Called when an RGB slider is changed (to lazy to rename)
    def hsvSliderChanged(self, slider, label):
        sliderVal = slider[0].value()
        slider[1] = sliderVal
        label.setText(str(sliderVal))
        self.updated = False
    
    # Called when a slider that is continuous is changed
    def ratioSliderChanged(self, slider, label):
        sliderVal = slider[0].value() / 100.0
        slider[1] = sliderVal
        label.setText(str(sliderVal))
        self.updated = False
    
    def approxSliderChanged(self, slider, label):
        sliderVal = slider[0].value() / 10.0
        slider[1] = sliderVal
        label.setText(str(sliderVal))
        self.updated = False

    def aspectComboChanged(self):
        self.aspect = self.comboAspect.currentText()
        self.updated = False

    # If a checkbox is changed, signal an update    
    def checkboxChanged(self):
        self.updated = False
    
    # If the button to add an angle to the list view is clicked
    def addAngleClicked(self):
        angleText = self.editAddAngle.text()
        if len(angleText) > 0:
            self.listAngle.addItems([angleText])
        self.updated = False
    
    # If an angle is selected and remove is clicked
    def removeAngleClicked(self):
        items = self.listAngle.selectedItems()

        for i in items:
            self.listAngle.takeItem(self.listAngle.row(i))
        self.updated = False

    # Main loop for the thread
    def run(self):
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
                    print("---------- Updating ----------")
                    bgr_frame = cv2.imread(imgPaths[self.imgIndx])
                    self.processImage(bgr_frame)
                    self.updated = True
        elif self.mode == "Stream":
            cap = cv2.VideoCapture("http://frcvision.local:1181/stream.mjpg")
            while self.deleted is False:
                ret, bgr_frame = cap.read()

                self.processImage(bgr_frame)
                # convertToQtFormat = QImage(bgr_frame, bgr_frame.shape[1], bgr_frame.shape[0], bgr_frame.shape[1] * 3, QImage.Format_RGB888)
                # p = convertToQtFormat.scaled(480, 360)  
                # self.imageSignal.emit(p) 
            # stream = urllib.urlopen('http://frcvision.local:1181/stream.mjpg')
            # bytes = ''
            # while True:
            #     bytes += stream.read(1024)
            #     a = bytes.find('\xff\xd8')
            #     b = bytes.find('\xff\xd9')
            #     if a != -1 and b != -1:
            #         jpg = bytes[a:b+2]
            #         bytes = bytes[b+2:]
            #         img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            #         convertToQtFormat = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
            #         p = convertToQtFormat.scaled(480, 360)  
            #         self.imageSignal.emit(p)    

    # Processes the given image and signals the main thread of the change
    def processImage(self, img):

        kernel = np.ones((self.morphKernel[1],self.morphKernel[1]),np.uint8)

        (cb, cg, cr) = cv2.split(img)
        bluePlusRed = cv2.addWeighted(cb, self.channelB[1] / 100.0, cr, self.channelR[1] / 100.0, 0.0)
        imageOut = cv2.subtract(cg, bluePlusRed)

        erosion = cv2.erode(imageOut,kernel,iterations = self.morphIteration[1])
        dialate = cv2.erode(erosion,kernel,iterations = self.morphIteration[1])

        thresholdVal,th2 = cv2.threshold(dialate,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        if thresholdVal < self.channelOtsu[1]:
            print("false")
        
        _, contours, _ = cv2.findContours(th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        i = 0
        for cnt in contours:
            solidity = self.getSolidity(cnt)
            extent = self.getExtent(cnt)
            aspect = self.getAspectRatio(cnt)
            orientation = self.getOrientation(cnt)
            sides = self.getSides(cnt)
            validAngle = self.validAngle(orientation)

            area = cv2.contourArea(cnt)
            if self.solL[1] <= solidity <= self.solH[1]:
                if self.extL[1] <= extent <= self.extH[1]:
                    if self.sideMin[1] <= sides <= self.sideMax[1]:
                        if validAngle:
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
                                self.drawID(cnt, img, i, aspect)
                                i += 1
                                if contourDrawn and orientation is not None:
                                    if self.checkAngle.isChecked():
                                        self.drawAngles(cnt, img, orientation)

        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # res = cv2.bitwise_and(rgb_frame, rgb_frame, mask= mask)
        convertToQtFormat = QImage(rgb_frame, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(480, 360)
        
        self.imageSignal.emit(p)  

    def drawID(self, cnt, img, i, aspect):
        if self.contourInfoCheck.isChecked():
            print("----- Contour {} -----".format(i))
            print("Area: {}".format(cv2.contourArea(cnt)))
            print("Aspect Ratio: {}".format(aspect))
            x,y,w,h = cv2.boundingRect(cnt)
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.putText(img, str(i), (cx, int(cy-h/2)), cv2.FONT_HERSHEY_SIMPLEX, .4, (255, 255, 255), 1, cv2.LINE_AA)
    
    # Draws the angle of the orientation for each contour
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
    
    # Returns the solidity of a contour (ratio of area to convex hull)
    def getSolidity(self, cnt):
        area = cv2.contourArea(cnt)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area != 0:
           return float(area)/hull_area
        return 0
    
    # Returns the extent of a contour (ratio of area to bounding rectangle area)
    def getExtent(self, cnt):
        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        rect_area = w*h
        if rect_area != 0:
            return float(area)/rect_area
        return 0

    # Returns the aspect ratio of a contour (ratio of width to height)
    def getAspectRatio(self, cnt):
        x,y,w,h = cv2.boundingRect(cnt)
        if h != 0:
            return float(w)/h
        return None
    
    def getOrientation(self, cnt):
        if (len(cnt) >= 5):
            (x, y),(MA, ma),angle = cv2.fitEllipse(cnt)
            return angle
        return None
    
    # Returns an estimate of the number of sides a shape has
    def getSides(self, cnt):
        epsilon = self.sideApprox[1]*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        return len(approx)
    
    # Determines if an angle is valid based on the list and tolerance value
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

    # Call this when you want to change the mode
    def pauseThread(self):
        self.deleted = True
    
    # Call this after calling pauseThread and setMode to restart the tread
    def continueThread(self):
        t = threading.Timer(.5,self.enableThread,args=[])
        t.start()
    
    # Called from continueThread after a .5 second delay. This is a band-aid fix to an underlying problem
    # in the QThreading structure. (The .5 second delay makes sure at least one iteration of the main loop has
    # run in order to properly reset some flags. The delay might need to be changed to support lower end hardware)
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

        self.videoSource = self.ui.findChild(QLabel, 'videoSource')
        
        self.comboSource = self.ui.findChild(QComboBox, 'comboSource')
        self.comboSource.currentTextChanged.connect(self.signal_comboChanged)

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

    def signal_comboChanged(self, value):
        sourceMode = self.comboSource.currentText()
        self.cvThread.pauseThread()
        if sourceMode == "Video":
            self.layout_toggle(self.layoutVideo, True)
            self.layout_toggle(self.layoutFolder, False)

            self.cvThread.setMode(sourceMode)
            self.cvThread.continueThread()
        elif sourceMode == "Folder":
            self.layout_toggle(self.layoutVideo, False)
            self.layout_toggle(self.layoutFolder, True)

            self.cvThread.setMode(sourceMode)
            self.cvThread.continueThread()
        elif sourceMode == "Stream":
            self.layout_toggle(self.layoutVideo, False)
            self.layout_toggle(self.layoutFolder, False)

            self.cvThread.setMode(sourceMode)
            self.cvThread.continueThread()
        elif sourceMode == "None":
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