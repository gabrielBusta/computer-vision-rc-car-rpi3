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
import sys
import cv2
from settings import *
from cvutils import *
from curses import wrapper, A_BOLD


def main(stdscr):
    stdscr.addstr(1, 1, 'SELF DRIVING GOPIGO', A_BOLD)
    stdscr.refresh()
    #video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    video = VideoStream('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT)).start()
    streaming, frame = video.read()

    if streaming:
        #cv2.namedWindow('GOPIGO')
        #cv2.namedWindow('ROI')

        speedSignClassifier = cv2.CascadeClassifier('speed-sign-haar-cascade.xml')
        stopSignClassifier = cv2.CascadeClassifier('stop-sign-haar-cascade.xml')
        imageAnalysis = ImageAnalysis(frame.shape, stopSignClassifier, speedSignClassifier)

        fpsTimer = FPSTimer().start()

        while streaming:
            gray = imageAnalysis.grayScale(frame)
            blur = imageAnalysis.gaussianBlur(gray)
            threshold = imageAnalysis.invertedBinaryThreshold(blur,
                                                              lowerBound=90,
                                                              upperBound=255)
            lanes = imageAnalysis.detectLanes(blur)
            speedSigns = imageAnalysis.detectSpeedSigns(blur)
            stopSigns = imageAnalysis.detectStopSigns(blur)
            speedSignDigitsROI = imageAnalysis.readDigits(threshold, speedSigns)

            imageAnalysis.drawLanes(frame, lanes)
            imageAnalysis.drawSpeedSigns(frame, speedSigns)
            imageAnalysis.drawStopSigns(frame, stopSigns)
            #cv2.imshow('GOPIGO', frame)
            #cv2.imshow('ROI', speedSignDigitsROI)
            #cv2.waitKey(1)
            streaming, frame = video.read()
            fpsTimer.update()

        fpsTimer.stop()

        stdscr.addstr(3, 1, '[INFO] elasped time: {:.2f}'.format(fpsTimer.elapsed()))
        stdscr.addstr(4, 1, '[INFO] approx. FPS: {:.2f}'.format(fpsTimer.fps()))
        stdscr.addstr(6, 1, 'Hit SPACE to quit...')
        stdscr.refresh()
        while True:
            c = chr(stdscr.getch())
            if c == ' ':
                break

    cv2.destroyAllWindows()
    video.release()

if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0
    wrapper(main)
