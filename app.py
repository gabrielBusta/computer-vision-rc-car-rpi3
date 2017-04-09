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


def main():
    workers = []

    if CAMERA_ON:
        workers.append(Process(target=vision,
                               name='VisionProcess'))
    if ULTRASONIC_SENSOR_ON:
        workers.append(Process(target=ultrasonic_sense,
                               name='UltrasonicSenseProcess'))

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()


def ultrasonic_sense():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((ROBOT_IP, ULTRASONIC_SENSOR_PORT))
    try:
        message = connection.recv(1024).decode()
        # the first few messages might be the empty string.
        while not message:
            message = connection.recv(1024).decode()
        while True:
            message = connection.recv(1024).decode()
            # when the ultrasonic sensor stream stops it sends an empty string.
            if not message:
                break
            distance = int(message)
    finally:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()


def vision():
    speed_sign_cascade = cv2.CascadeClassifier('speed-sign-haar-cascade.xml')
    stop_sign_cascade = cv2.CascadeClassifier('stop-sign-cascade.xml')
    video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    cv2.namedWindow(ROBOT_IP, cv2.WINDOW_NORMAL)
    cv2.namedWindow('ROI', cv2.WINDOW_NORMAL)
    try:
        streaming, frame = video.read()
        while streaming:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            speed_signs = speed_sign_cascade.detectMultiScale(blurred, 1.3, 5)
            stop_signs = stop_sign_cascade.detectMultiScale(blurred, 1.3, 5)
            for x, y, w, h in speed_signs:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_blurred = blurred[y:y+h, x:x+w]
                ret_val, roi_th = cv2.threshold(roi_blurred, 90, 255, cv2.THRESH_BINARY_INV)
                cv2.imshow('ROI', roi_th)
            for x, y, w, h in stop_signs:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            drawbanner(frame)
            cv2.imshow(ROBOT_IP, frame)
            cv2.waitKey(1)
            streaming, frame = video.read()
    finally:
        video.release()
        cv2.destroyAllWindows()


def drawbanner(frame):
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (255, 255, 255)
    scale = 1
    thickness = 2
    text = 'Selfdriving GoPiGo'
    pos = (175, 450)
    cv2.putText(frame, text, pos, font, scale, color, thickness, cv2.LINE_AA)


if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0
    main()
