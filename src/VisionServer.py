#!/usr/bin/env python3
# Import the camera server
from cscore import CameraServer, CvSink, UsbCamera, CvSource
import time
from networktables import NetworkTables
import logging
import threading
import math
import numpy as np
import cv2

resolution = (320, 240)
teamNumber = 4500

R = 1
B = 1

morphIteration = 0
kernelSize = 0

solidityHigh = 1.0
solidityLow = 0

extentHigh = 1.0
extentLow = 0

sidesHigh = 15
sidesLow = 0
sidesApprox = 0.04

aspectRatio = "<" # w {> or < or N/A } h

angleList = []
angleTolerance = 10

class CVThread(threading.Thread):
    def __init__(self, name, camera, sd):
        threading.Thread.__init__(self)
        self.name = name
        self.camera = camera
        # SmartDashboard instance
        self.sd = sd
        self.imgBase = np.zeros(shape=(resolution[1], resolution[0], 3), dtype=np.uint8)
    

    def run(self):
        while True:
            time, img = self.camera.getFrame(self.imgBase)
            if time == 0:
                self.camera.getOutputStream().notifyError(self.camera.getCvSink().getError())
                continue
    
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
        epsilon = sidesApprox*cv2.arcLength(cnt,True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        return len(approx)
    
    # Determines if an angle is valid based on the list and tolerance value
    def validAngle(self, orientation):
        try:
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

class USBCamera:
    def __init__(self, port, instance: CameraServer, streamName):
        self.port = port
        self.instance = instance
        self.usb = self.instance.startAutomaticCapture(dev=port)
        self.cvSink = self.instance.getVideo(camera=self.usb)
        self.usb.setResolution(resolution[0], resolution[1])
        self.outputStream = self.instance.putVideo(streamName, resolution[0], resolution[1])
        
    def getCamera(self) -> UsbCamera:
        return self.usb

    def getCvSink(self) -> CvSink:
        return self.cvSink

    def getFrame(self, img):
        return self.cvSink.grabFrame(img)
    
    def getOutputStream(self) -> CvSource:
        return self.outputStream


def main():
    logging.basicConfig(level=logging.DEBUG)
    
    NetworkTables.initialize(server='roborio-{}-frc.local'.format(teamNumber))
    sd = NetworkTables.getTable('SmartDashboard')
    sd.putNumber("imgW", resolution[0])
    sd.putNumber("imgH", resolution[1])
    
    cs = CameraServer.getInstance()
    cs.enableLogging()

    camOne = USBCamera(0, cs, "OpenCV_One")

    camOneThread = CVThread("OpenCV_One", camOne, sd)
    camOneThread.start()

if __name__ == "__main__":
    main()
