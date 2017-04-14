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
import logging
from plumbum import colors
from cvutils import *
from settings import *


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def main():
    #videoStream = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    #videoStream = VideoStream('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT)).start()
    videoStream = VideoStream(0).start()
    streaming, frame = videoStream.read()
    logger.debug('Video stream started.')

    speedSignClassifier = cv2.CascadeClassifier('speed-sign-haar-cascade.xml')
    stopSignClassifier = cv2.CascadeClassifier('stop-sign-haar-cascade.xml')
    logger.debug('HAAR cascades loaded successfully.')

    imageAnalysis = ImageAnalysis(frame.shape,
                                  stopSignClassifier,
                                  speedSignClassifier)

    displayManager = DisplayManager()

    displayManager.createWindows()

    fpsTimer = FPSTimer().start()

    # MAIN LOOP #
    while streaming:
        gray = imageAnalysis.grayScale(frame)
        blur = imageAnalysis.gaussianBlur(gray)
        threshold = imageAnalysis.invertedBinaryThreshold(blur,
                                                          lowerBound=90,
                                                          upperBound=255)
        lanes = imageAnalysis.detectLanes(blur)
        speedSigns = imageAnalysis.detectSpeedSigns(blur)
        stopSigns = imageAnalysis.detectStopSigns(blur)
        digitsRoi = imageAnalysis.readDigits(threshold, speedSigns)

        displayManager.drawLanes(frame, lanes)
        displayManager.drawSpeedSigns(frame, speedSigns)
        displayManager.drawStopSigns(frame, stopSigns)
        displayManager.show(frame, digitsRoi)

        if displayManager.getKeyPressed() == 'q':
            break

        streaming, frame = videoStream.read()
        fpsTimer.update()

    fpsTimer.stop()

    logger.info(colors.blue & colors.bold |
                'Elasped time = {:.2f}'
                .format(fpsTimer.elapsed()))

    logger.info(colors.blue & colors.bold |
                'Approx. FPS = {:.2f}'.format(fpsTimer.fps()))

    displayManager.destroyWindows()
    videoStream.release()


if __name__ == '__main__':
    main()
