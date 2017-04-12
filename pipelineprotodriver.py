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
# from cvutils import *
from pipelineproto import *
from curses import wrapper, A_BOLD
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def main():
    logger.info('creating the preview window.')
    cv2.namedWindow('GOPIGO')
    cv2.namedWindow('ROI')

    # video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    logger.info('loading HAAR cascades.')
    speedSignClassifier = cv2.CascadeClassifier('speed-sign-haar-cascade.xml')
    stopSignClassifier = cv2.CascadeClassifier('stop-sign-haar-cascade.xml')

    logger.info('creating video stream and image analysis object.')
    videoStream = VideoStream('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    imageAnalysis = ImageAnalysis(stopSignClassifier, speedSignClassifier, videoStream).start()

    logger.info('streaming video.')
    fpsTimer = FPSTimer().start()

    while imageAnalysis.videoStreaming:
        #cv2.imshow('GOPIGO', imageAnalysis.processedFrame)
        cv2.waitKey(1)
        fpsTimer.update()

    fpsTimer.stop()

    #stdscr.addstr(3, 1, '[INFO] elasped time: {:.2f}'.format(fpsTimer.elapsed()))
    #stdscr.addstr(4, 1, '[INFO] approx. FPS: {:.2f}'.format(fpsTimer.fps()))
    #stdscr.addstr(6, 1, 'Hit SPACE to quit...')
    #stdscr.refresh()
   # while True:
  #      c = chr(stdscr.getch())
 #       if c == ' ':
#            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0
    #wrapper(main)
    main()
