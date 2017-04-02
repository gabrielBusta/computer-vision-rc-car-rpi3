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


def main():
    exit = Event()
    processes = []
    processes.append(Process(target=camera,
                             name='camera',
                             args=(exit, ('', CAMERA_PORT))))
    processes.append(Process(target=ultrasonic_sensor,
                             name='ultrasonic sensor',
                             args=(exit, ('', ULTRASONIC_SENSOR_PORT))))
    processes.append(Process(target=remote_control,
                             name='remote control',
                             args=(exit, ('', REMOTE_CONTROL_PORT))))
    start(processes)
    try:
        spin()
    except KeyboardInterrupt:
        exit.set()
        wait_on(processes)
    except Exception as ex:
        print_exception(ex)
        exit.set()
        wait_on(processes)


def spin():
    while True:
        time.sleep(0.1)


def camera(exit, address):
    server = new_server(address)
    connection, _ = server.accept()
    stream = connection.makefile('wb')
    camera = PiCamera()
    camera.framerate = CAMERA_SETTINGS['FRAMERATE']
    camera.resolution = CAMERA_SETTINGS['RESOLUTION']
    camera.rotation = CAMERA_SETTINGS['ROTATION']
    camera.start_recording(stream, format=CAMERA_SETTINGS['FORMAT'])
    try:
        while not exit.is_set():
            camera.wait_recording(1)
    except Exception as ex:
        print_exception(ex)
    finally:
        camera.close()
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        server.shutdown(socket.SHUT_RDWR)
        server.close()


def ultrasonic_sensor(exit, address):
    server = new_server(address)
    connection, _ = server.accept()
    try:
        while not exit.is_set():
            distance = str(gopigo.us_dist(gopigo.analogPort))
            connection.send(distance.encode())
            time.sleep(0.1)
    except Exception as ex:
        print_exception(ex)
    finally:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        server.shutdown(socket.SHUT_RDWR)
        server.close()


def remote_control(exit, address):
    commands = {
        'fwd': gopigo.fwd,
        'bwd': gopigo.bwd,
        'left': gopigo.left,
        'right': gopigo.right,
        'stop': gopigo.stop
    }
    server = new_server(address)
    connection, _ = server.accept()
    while not exit.is_set():
        try:
            msg = connection.recv(1024).decode()
        except socket.timeout:
            continue
        except Exception as ex:
            print_exception(ex)
        else:
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


def start(processes):
    for process in processes:
        process.start()


def wait_on(processes):
    for process in processes:
        process.join()


def print_exception(ex):
    sys.stdout.write('[{}]: {}\n'.format(current_process().name, repr(ex)))


if __name__ == '__main__':
    main()
