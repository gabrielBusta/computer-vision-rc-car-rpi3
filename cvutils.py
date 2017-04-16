#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Gabriel Bustamante
Email: gabrielbusta@gmail.com

Selfdriving GoPiGo: An open source self-driving robot application.
This app was built using the GoPiGo robotics platform for the Raspberry Pi.

Copyright (C) 2017 Gabriel Bustamante
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
"""
import datetime
import cv2
import numpy as np
import logging
from plumbum import colors
from threading import Thread


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ImageAnalysis(object):
    def __init__(self, shape, stopSignCascade, speedSignCascade, laneRoiCutoff=390,
                 stopSignScaleFactor=1.3, stopSignMinNeighbors=5,
                 speedSignScaleFactor=1.3, speedSignMinNeighbors=5):

        self.height, self.width, self.channels = shape

        self.speedSignClassifier = cv2.CascadeClassifier(speedSignCascade)
        self.stopSignScaleFactor = stopSignScaleFactor
        self.stopSignMinNeighbors = stopSignMinNeighbors

        logger.info(colors.blue & colors.bold |
                    'Stop sign cascade classifier: '
                    'scale factor = {}, minimum number of neighbors = {}'
                    .format(self.stopSignScaleFactor,
                            self.stopSignMinNeighbors))

        self.stopSignClassifier = cv2.CascadeClassifier(stopSignCascade)
        self.speedSignScaleFactor = speedSignScaleFactor
        self.speedSignMinNeighbors = speedSignMinNeighbors

        logger.info(colors.blue & colors.bold |
                    'Speed sign cascade classifier: '
                    'scale factor = {}, minimum number of neighbors = {}'
                    .format(self.speedSignScaleFactor,
                            self.speedSignMinNeighbors))

        logger.debug('HAAR cascades loaded successfully.')

        self.laneRoiCutoff = laneRoiCutoff


    def gaussianBlur(self, frame, kernelSize=(5, 5), sigma=0):
        return cv2.GaussianBlur(frame, kernelSize, sigma)

    def grayScale(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def invertedBinaryThreshold(self, frame, lowerBound, upperBound):
        ret, thresholded = cv2.threshold(frame, lowerBound, upperBound,
                                         cv2.THRESH_BINARY_INV)
        return thresholded

    def openWithEllipticalKernel(self, frame, kernelSize=(1, 5)):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernelSize)
        return cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

    def resize(self, frame, size):
        roi = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

    def dilate(self, frame, kernel=(1, 1)):
        cv2.dilate(frame, kernel)

    def detectLanes(self, frame):
        roi = frame[self.laneRoiCutoff:self.height, 0:self.width]
        roi_canny = cv2.Canny(frame, 90, 200)
        lanes = cv2.HoughLinesP(roi_canny,
                                1,
                                np.pi / 180,
                                30,
                                np.array([]),
                                minLineLength=20,
                                maxLineGap=20)
        return lanes

    def detectSpeedSigns(self, frame):
        return self.speedSignClassifier.detectMultiScale(frame,
                                                         self.speedSignScaleFactor,
                                                         self.speedSignMinNeighbors)

    def detectStopSigns(self, frame):
        return self.stopSignClassifier.detectMultiScale(frame,
                                                        self.stopSignScaleFactor,
                                                        self.stopSignMinNeighbors)

    def readDigits(self, frame, signs):
        for x, y, w, h in signs:
            sign = frame[y:y+h, x:x+w]

            return sign

        return np.zeros((self.height, self.width, self.channels))


class DisplayManager(object):
    def __init__(self, lineThickness=3, font=cv2.FONT_HERSHEY_SIMPLEX,
                 fontThickness=1, fontScale=1, laneRoiOffset=390):

        self.BLUE = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (0, 0, 255)

        self.lineThickness = lineThickness
        self.font = font
        self.fontThickness = fontThickness
        self.fontScale = fontScale
        self.laneRoiOffset = laneRoiOffset

    def createWindows(self):
        cv2.namedWindow('GOPIGO')
        cv2.namedWindow('ROI')

    def destroyWindows(self):
        cv2.destroyAllWindows()

    def show(self, frame, digitsRoi):
        cv2.imshow('GOPIGO', frame)
        cv2.imshow('ROI', digitsRoi)

    def getKeyPressed(self):
        return chr(cv2.waitKey(1))

    def drawLanes(self, frame, lanes):
        if lanes is not None:
            for lane in lanes:
                for x1, y1, x2, y2 in lane:
                    cv2.line(frame,
                             (x1, y1 + self.laneRoiOffset),
                             (x2, y2 + self.laneRoiOffset),
                             self.BLUE,
                             self.lineThickness)

    def drawSpeedSigns(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          self.GREEN, self.lineThickness)
            cv2.putText(frame, 'Speed Limit', (x, y - 8), self.font,
                        1, self.GREEN, self.fontThickness, cv2.LINE_AA)

    def drawStopSigns(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          self.RED, self.lineThickness)
            cv2.putText(frame, 'Stop!', (x, y - 8), self.font, self.fontScale,
                        self.RED, self.fontThickness, cv2.LINE_AA)


class VideoStream(object):
    def __init__(self, url):
        self.stream = cv2.VideoCapture(url)
        self.streaming, self.frame = self.stream.read()
        self.shutdownRequest = False

    def start(self):
        self.thread = Thread(target=self.update)
        self.thread.start()
        return self

    def update(self):
        while not self.shutdownRequest:
            self.streaming, self.frame = self.stream.read()

    def read(self):
        return self.streaming, self.frame

    def release(self):
        self.shutdownRequest = True
        self.thread.join()
        self.stream.release()


class FPSTimer(object):
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.numFrames = 0

    def start(self):
        self.startTime = datetime.datetime.now()
        return self

    def stop(self):
        self.endTime = datetime.datetime.now()

    def update(self):
        self.numFrames += 1

    def elapsed(self):
        return (self.endTime - self.startTime).total_seconds()

    def fps(self):
        return self.numFrames / self.elapsed()
