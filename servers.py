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
from curses import wrapper, A_BOLD
from picamera import PiCamera
from settings import *
from utils import Server


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

    stdscr.addstr(3, 1, '[INFO] Wating for CV client...')
    stdscr.refresh()
    cameraServer.start()
    stdscr.addstr(3, 25, 'connection with CV client established.')
    stdscr.refresh()


    stdscr.addstr(5, 1, 'Hit SPACE to quit...')
    stdscr.refresh()
    while True:
        c = chr(stdscr.getch())
        if c == ' ':
            cameraServer.shutdown()
            break


# Each handle is executed in it's own independent process.

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


if __name__ == '__main__':
    wrapper(main)
