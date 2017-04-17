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
import settings
from utils import RemoteControl
from plumbum import colors
from cvutils import *


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    url = 'tcp://{}:{}'.format(settings.ROBOT_IP, settings.CAMERA_PORT)
    #video_stream = cv2.VideoCapture(url)
    #remote_control = RemoteControl(settings.ROBOT_IP, settings.REMOTE_CONTROL_PORT)
    video_stream = VideoStream(0).start()
    streaming, frame = video_stream.read()

    logger.debug('Video stream started.')

    analysis = Analysis(frame.shape,
                        'stop-sign-haar-cascade.xml',
                        'speed-sign-haar-cascade.xml')

    logger.debug('Sucessfully initialized '
                 'image analysis control object.')

    display = Display()

    logger.debug('Sucessfully initialized display manager boundary object.')

    display.create_windows()

    fps_timer = FPSTimer().start()

    # MAIN LOOP #
    while streaming:
        grayed = analysis.gray_scale(frame)
        blurred = analysis.gaussian_blur(grayed)

        lanes = analysis.detect_lanes(blurred)
        speed_signs = analysis.detect_speed_signs(blurred)
        stop_signs = analysis.detect_stop_signs(blurred)

        display.draw_lanes(frame, lanes)
        display.draw_speed_signs(frame, speed_signs)
        display.draw_stop_signs(frame, stop_signs)
        display.show(frame)

        if display.get_key_pressed() == 'q':
            break

        streaming, frame = video_stream.read()
        fps_timer.update()

    fps_timer.stop()

    logger.info(colors.blue & colors.bold |
                'Elasped time = {:.2f}'
                .format(fps_timer.elapsed()))

    logger.info(colors.blue & colors.bold |
                'Approx. FPS = {:.2f}'.format(fps_timer.fps()))

    display.destroy_windows()
    video_stream.release()


if __name__ == '__main__':
    main()
