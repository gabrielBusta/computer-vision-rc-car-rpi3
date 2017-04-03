#!/usr/bin/env python3
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
import socket
import gopigo
import time
import sys
from multiprocessing import Process, Event, current_process
from picamera import PiCamera
from settings import *


exit_flag = Event()


def main():
    workers = []

    if CAMERA_ON:
        workers.append(Process(target=stream_camera,
                               name='CameraProcess'))
    if ULTRASONIC_SENSOR_ON:
        workers.append(Process(target=stream_ultrasonic_sensor,
                               name='UltrasonicSensorProcess'))
    if REMOTE_CONTROL_ON:
        workers.append(Process(target=listen_to_remote_control,
                               name='RemoteControlProcess'))

    for worker in workers:
        worker.start()


def stream_camera():
    server = new_server(('', CAMERA_PORT))
    connection, _ = server.accept()
    stream = connection.makefile('wb')
    camera = PiCamera()
    camera.framerate = CAMERA_FRAMERATE
    camera.resolution = CAMERA_RESOLUTION
    camera.rotation = CAMERA_ROTATION
    camera.start_recording(stream, format=CAMERA_VIDEO_FORMAT)
    try:
        while True:
            camera.wait_recording(1)
    finally:
        camera.close()
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        server.shutdown(socket.SHUT_RDWR)
        server.close()


def stream_ultrasonic_sensor():
    server = new_server(('', ULTRASONIC_SENSOR_PORT))
    connection, _ = server.accept()
    try:
        while True:
            distance = str(gopigo.us_dist(gopigo.analogPort))
            connection.send(distance.encode())
            time.sleep(0.1)
    finally:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        server.shutdown(socket.SHUT_RDWR)
        server.close()


def listen_to_remote_control():
    commands = {
        'fwd': gopigo.fwd,
        'bwd': gopigo.bwd,
        'left': gopigo.left,
        'right': gopigo.right,
        'stop': gopigo.stop
    }
    server = new_server(('', REMOTE_CONTROL_PORT))
    connection, _ = server.accept()
    try:
        while True:
            msg = connection.recv(1024).decode()
            command = commands[msg]
            command()
    finally:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        server.shutdown(socket.SHUT_RDWR)
        server.close()


def new_server(address):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    server.listen(0)
    return server


if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0
    main()
