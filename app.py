#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The following code is based on a design described by Joseph Howse in
OpenCV Computer Vision with Python (Birmingham: Packt Publishing, 2013).
See Appendix A (Integrating Pygame).

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
from managers import PygameWindowManager as WindowManager, CaptureManager


class App(object):
    def __init__(self, video_source):
        self._windowManager = WindowManager(video_source, self.onKeypress)
        capture = cv2.VideoCapture(video_source)
        self._captureManager = CaptureManager(capture, self._windowManager, True)

    def run(self):
        """Run the main loop."""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame

            if frame is not None:
                # TODO: Filter the frame
                pass

            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self, keycode):
        """Handle a keypress.
        space  -> Take a screenshot.
        tab    -> Start/stop recording a screencast.
        escape -> Quit.
        """
        if keycode == 32: # space
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9: # tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo('screencast.avi')
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 27: # escape
            self._windowManager.destroyWindow()


if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0

    url = 'tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT)
    app = App(url)
    app.run()
