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
import cv2
import socket
import sys
import numpy as np
from multiprocessing import Process, Lock
from remote import RemoteController
from settings import *
from cvutils import *


def main():
    cv2.namedWindow('GOPIGO', cv2.WINDOW_NORMAL)
    cv2.namedWindow('ROI', cv2.WINDOW_NORMAL)
    video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    try:
        streaming, frame = video.read()
        if streaming:
            speedSignClassifier = cv2.CascadeClassifier('speed-sign-haar-cascade.xml')
            stopSignClassifier = cv2.CascadeClassifier('stop-sign-haar-cascade.xml')
            cvManager = CVManager(frame.shape, stopSignClassifier, speedSignClassifier)
            while streaming:
                gray = GrayScale(frame)
                blur = GaussianBlur(gray)
                threshold = InvertedBinaryThreshold(blur, lowerBound=90, upperBound=255)
                lanes = cvManager.detectLanes(blur)
                speedSigns = cvManager.detectSpeedSigns(blur)
                stopSigns = cvManager.detectStopSigns(blur)
                speedSignDigits = cvManager.readDigits(threshold, speedSigns)
                cvManager.drawLanes(frame, lanes)
                cvManager.drawSpeedSigns(frame, speedSigns)
                cvManager.drawStopSigns(frame, stopSigns)
                cv2.imshow('GOPIGO', frame)
                cv2.imshow('ROI', speedSignDigits)
                cv2.waitKey(1)
                streaming, frame = video.read()
    finally:
        video.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0
    main()
