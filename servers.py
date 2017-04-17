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
import settings
import logging
from plumbum import colors
from picamera import PiCamera
from utils import Server


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def main():
    logger.debug('Servers waiting for external connections.')
    camera_server = Server('',
                           settings.CAMERA_PORT,
                           camera_handle,
                           name='CameraServer').start()

    remote_control_server = Server('',
                                   settings.REMOTE_CONTROL_PORT,
                                   remote_control_handle,
                                   name='RemoteControlServer').start()

    print(colors.green & colors.bold |
          '\n *******************************\n'
            ' *                             *\n'
            ' *     PRESS ENTER TO QUIT     *\n'
            ' *                             *\n'
            ' *******************************\n')

    input()
    camera_server.shutdown()
    remote_control_server.shutdown()


# Each handle is executed in it's own independent process.
def remote_control_handle(connection, shutdown_request, addr):
    logger = logging.getLogger('RemoteControlHandle')
    logging.basicConfig(level=logging.DEBUG)
    commands = {
        'fwd': gopigo.fwd,
        'bwd': gopigo.bwd,
        'left': gopigo.left,
        'right': gopigo.right,
        'stop': gopigo.stop
    }

    logger.info(colors.blue & colors.bold |
                'Listening to remote control commands from {}'
                .format(addr))

    while not shutdown_request.is_set():
        message = connection.recv(1024).decode()
        if not message:
            break
        command = commands[message]
        command()

    logger.warn(colors.yellow & colors.bold |
                'Stopped listening to remote control commands from {}'
                .format(addr))


# Each handle is executed in it's own independent process.
def camera_handle(connection, shutdown_request, addr):
    logger = logging.getLogger('CameraHandle')
    logging.basicConfig(level=logging.DEBUG)
    stream = connection.makefile('wb')
    camera = PiCamera()
    camera.framerate = settings.CAMERA_FRAMERATE
    camera.resolution = settings.CAMERA_RESOLUTION
    camera.rotation = settings.CAMERA_ROTATION

    camera.start_recording(stream, format=settings.CAMERA_VIDEO_FORMAT)
    logger.info(colors.blue & colors.bold |
                'Streaming video to {}'
                .format(addr))
    try:
        while not shutdown_request.is_set():
            camera.wait_recording(1)
    except Exception as ex:
            logger.warn(colors.yellow & colors.bold | ex)
    finally:
        try:
            camera.close()
        except Exception as ex:
            logger.warn(colors.yellow & colors.bold | ex)

    logger.info(colors.blue & colors.bold |
                'Stopped stream video too {}'
                .format(addr))

if __name__ == '__main__':
    main()
