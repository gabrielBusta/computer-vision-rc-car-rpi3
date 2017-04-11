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
import socket
import gopigo
import sys
from curses import wrapper, A_BOLD
from multiprocessing import Process, Event
from picamera import PiCamera
from settings import *


def main(stdscr):
    stdscr.addstr(1, 1, 'SELF DRIVING GOPIGO', A_BOLD)
    stdscr.refresh()

    cameraServer = Server('',
                          CAMERA_PORT,
                          HandleCamera,
                          name='cameraServer')
    remoteControlServer = Server('',
                                 REMOTE_CONTROL_PORT,
                                 HandleRemoteControl,
                                 name='remoteControlServer')

    stdscr.addstr(3, 1, 'Wating for CV client...')
    stdscr.refresh()
    cameraServer.start()
    stdscr.addstr(3, 25, 'connection with CV client established.')
    stdscr.refresh()

    stdscr.addstr(4, 1, 'Wating for remote control client...')
    stdscr.refresh()
    remoteControlServer.start()
    stdscr.addstr(4, 37, 'connection with remote control client established.')
    stdscr.refresh()

    stdscr.addstr(6, 1, 'Hit SPACE to quit...')
    stdscr.refresh()
    while True:
        c = chr(stdscr.getch())
        if c == ' ':
            cameraServer.shutdown()
            remoteControlServer.shutdown()
            break


def HandleRemoteControl(connection, shutdownRequest):
    commands = {
        'fwd': gopigo.fwd,
        'bwd': gopigo.bwd,
        'left': gopigo.left,
        'right': gopigo.right,
        'stop': gopigo.stop
    }
    while not shutdownRequest.is_set():
        message = connection.recv(1024).decode()
        if not message:
            break
        command = commands[message]
        command()


def HandleCamera(connection, shutdownRequest):
    stream = connection.makefile('wb')
    camera = PiCamera()
    camera.framerate = CAMERA_FRAMERATE
    camera.resolution = CAMERA_RESOLUTION
    camera.rotation = CAMERA_ROTATION
    camera.start_recording(stream, format=CAMERA_VIDEO_FORMAT)
    try:
        while not shutdownRequest.is_set():
            camera.wait_recording(1)
    finally:
        camera.close()


class Server(object):
    def __init__(self, ip, port, handle, name):
        self.ip = ip
        self.port = port
        self.handle = handle
        self.name = name
        self.shutdownRequest = Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(0)
        self.connection, _ = self.socket.accept()
        self.process = Process(target=self.handle,
                               args=(self.connection, self.shutdownRequest),
                               name=self.name)
        self.process.start()

    def shutdown(self):
        self.shutdownRequest.set()
        self.process.join()
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


if __name__ == '__main__':
    if not DEBUG:
        sys.tracebacklimit = 0
    wrapper(main)
