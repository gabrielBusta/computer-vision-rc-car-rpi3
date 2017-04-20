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


class Analysis(object):
    def __init__(self, shape, stop_xml, speed_xml, lane_roi_cutoff=390,
                 stop_scale_factor=1.3, stop_min_neighbors=5,
                 speed_scale_factor=1.3, speed_min_neighbors=5):

        self.height, self.width, self.channels = shape

        self.speed_classifier = cv2.CascadeClassifier(speed_xml)
        self.stop_scale_factor = stop_scale_factor
        self.stop_min_neighbors = stop_min_neighbors

        logger.info(colors.blue & colors.bold |
                    'Stop sign cascade classifier: '
                    'scale factor = {}, minimum number of neighbors = {}'
                    .format(self.stop_scale_factor,
                            self.stop_min_neighbors))

        self.stop_classifier = cv2.CascadeClassifier(stop_xml)
        self.speed_scale_factor = speed_scale_factor
        self.speed_min_neighbors = speed_min_neighbors

        logger.info(colors.blue & colors.bold |
                    'Speed sign cascade classifier: '
                    'scale factor = {}, minimum number of neighbors = {}'
                    .format(self.speed_scale_factor,
                            self.speed_min_neighbors))

        logger.debug('HAAR cascades loaded successfully.')

        self.lane_roi_cutoff = lane_roi_cutoff


    def detect_lanes(self, frame):
        roi = frame[self.lane_roi_cutoff:self.height, 0:self.width]
        roi_canny = cv2.Canny(roi, 90, 200)
        lanes = cv2.HoughLinesP(roi_canny,
                                1,
                                np.pi / 180,
                                30,
                                np.array([]),
                                minLineLength=20,
                                maxLineGap=20)
        return lanes

    def detect_speed_signs(self, frame):
        return self.speed_classifier.detectMultiScale(frame,
                                                      self.speed_scale_factor,
                                                      self.speed_min_neighbors)

    def detect_stop_signs(self, frame):
        return self.stop_classifier.detectMultiScale(frame,
                                                     self.stop_scale_factor,
                                                     self.stop_min_neighbors)


    def gaussian_blur(self, frame, kernel_size=(5, 5), sigma=0):
        return cv2.GaussianBlur(frame, kernel_size, sigma)

    def gray_scale(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


class Display(object):
    def __init__(self, line_thickness=3, font=cv2.FONT_HERSHEY_SIMPLEX,
                 font_thickness=1, font_scale=1, lane_roi_offset=390):

        self.BLUE = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (0, 0, 255)

        self.line_thickness = line_thickness
        self.font = font
        self.font_thickness = font_thickness
        self.font_scale = font_scale
        self.lane_roi_offset = lane_roi_offset

    def create_windows(self):
        cv2.namedWindow('GOPIGO')

    def destroy_windows(self):
        cv2.destroyAllWindows()

    def show(self, frame):
        cv2.imshow('GOPIGO', frame)

    def get_key_pressed(self):
        return chr(cv2.waitKey(1))

    def draw_lanes(self, frame, lanes):
        if lanes is not None:
            for lane in lanes:
                for x1, y1, x2, y2 in lane:
                    cv2.line(frame,
                             (x1, y1 + self.lane_roi_offset),
                             (x2, y2 + self.lane_roi_offset),
                             self.BLUE,
                             self.line_thickness)

    def draw_speed_signs(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          self.GREEN, self.line_thickness)
            cv2.putText(frame, 'Speed Limit', (x, y - 8), self.font,
                        1, self.GREEN, self.font_thickness, cv2.LINE_AA)

    def draw_stop_signs(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          self.RED, self.line_thickness)
            cv2.putText(frame, 'Stop!', (x, y - 8), self.font, self.font_scale,
                        self.RED, self.font_thickness, cv2.LINE_AA)


class VideoStream(object):
    def __init__(self, url):
        self.stream = cv2.VideoCapture(url)
        self.streaming, self.frame = self.stream.read()

        if not self.streaming:
            logger.error(colors.red |
                        'VideoStream not started. Run "servers.py" on the GoPiGo!')
            exit(1)

        self.shutdown_request = False

    def start(self):
        self.thread = Thread(target=self.update)
        self.thread.start()
        return self

    def update(self):
        while not self.shutdown_request:
            self.streaming, self.frame = self.stream.read()

    def read(self):
        return self.streaming, self.frame

    def release(self):
        self.shutdown_request = True
        self.thread.join()
        self.stream.release()


class FPSTimer(object):
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.num_frames = 0

    def start(self):
        self.start_time = datetime.datetime.now()
        return self

    def stop(self):
        self.end_time = datetime.datetime.now()

    def update(self):
        self.num_frames += 1

    def elapsed(self):
        return (self.end_time - self.start_time).total_seconds()

    def fps(self):
        return self.num_frames / self.elapsed()
