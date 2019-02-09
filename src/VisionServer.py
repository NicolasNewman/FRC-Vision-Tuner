#!/usr/bin/env python3
# Import the camera server
from cscore import CameraServer, CvSink, UsbCamera, CvSource
import time
import math
from networktables import NetworkTables
import logging
import threading
import numpy as np
import cv2

resolution = (320, 240)
teamNumber = 4500

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
            angle = 0
            center = [0, 0]
            time, frame = self.camera.getFrame(self.imgBase)
            if time == 0:
                self.camera.getOutputStream().notifyError(self.camera.getCvSink().getError())
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret,th1 = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)

            _, cnts, _ = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            if len(cnts) > 0: 
                target = max(cnts, key = cv2.contourArea)
                if len(target) >= 5:
                    (x,y),(MA,ma),angle = cv2.fitEllipse(target)
                    if angle <= 180 and angle >= 90:
                        angle = angle - 180
                    M = cv2.moments(target)
                    x,y,w,h = cv2.boundingRect(target)
                    if M['m00'] != 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        center = [cx, cy]
                        orientationRad = (angle+270) * (math.pi / 180)
                        length = math.sqrt(w*w + h*h)/3
                        cv2.line(frame,(cx,cy),(int(cx+length*math.cos(orientationRad)),int(cy+length*math.sin(orientationRad))),(255,0,0),2)
                        # height, width = frame.shape[:2]
                    # arcLength = 2 * math.pi * (rR) * (angle / 360)
                    # encVal = (1024 * rR * (angle)) / (45 * dW)
                    # cv2.putText(frame, str(round(arcLength, 2)), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                    # cv2.putText(frame, str(round(encVal, 2)), (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(frame, str("({},{})".format(center[0], center[1])), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(frame, str(int(angle)), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

            self.sd.putNumber("rPI_angle", angle)
            self.sd.putNumberArray("rPI_center", center)
            self.camera.getOutputStream().putFrame(frame)
    
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
    
    # def getOrientation(self, cnt):
    #     if (len(cnt) >= 5):
    #         (x, y),(MA, ma),angle = cv2.fitEllipse(cnt)
    #         return angle
    #     return None
    
    # # Returns an estimate of the number of sides a shape has
    # def getSides(self, cnt):
    #     epsilon = sidesApprox*cv2.arcLength(cnt,True)
    #     approx = cv2.approxPolyDP(cnt,epsilon,True)
    #     return len(approx)
    
    # # Determines if an angle is valid based on the list and tolerance value
    # def validAngle(self, orientation):
    #     try:
    #         if len(angleList) >= 1:
    #             for angle in angleList:
    #                 if abs(angle - orientation) <= angleTolerance:
    #                     return True
    #             return False
    #         return True
    #     except ValueError:
    #         return True
    #     except TypeError:
    #         return True

class USBCamera:
    def __init__(self, port, instance: CameraServer, streamName):
        self.port = port
        self.instance = instance
        self.usb = self.instance.startAutomaticCapture(dev=port)
        # self.info = self.usb.getInfo()
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
    cs = CameraServer.getInstance()
    cs.enableLogging()

    camOne = USBCamera(0, cs, "OpenCV_One")

    # imgBase = np.zeros(shape=(resolution[1], resolution[0], 3), dtype=np.uint8)

    camOneThread = CVThread("OpenCV_One", camOne, sd)
    camOneThread.start()
    # while True:
    #     time, imgOne = camOne.getFrame(imgBase)
    #     if time == 0:
    #         camOne.getOutputStream().notifyError(camOne.getCvSink().getError())
    #         continue
    #     gray = cv2.cvtColor(imgOne, cv2.COLOR_BGR2GRAY)
        
    #     camOne.getOutputStream().putFrame(gray)

if __name__ == "__main__":
    main()
