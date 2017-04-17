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
import logging
from plumbum import colors
from threading import Thread
from multiprocessing import Process, Queue, Event, queues


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class RemoteControl(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_queue = Queue()
        self.shutdown_request = Event()

    def start(self):
        self.socket.connect((self.ip, self.port))
        self.process = Process(target=self.send_commands,
                               daemon=True)
        self.process.start()
        return self

    def send_commands(self):
        while not self.shutdown_request.is_set():
            try:
                command = self.command_queue.get(block=False)
                self.socket.send(command)
            except queues.Empty:
                continue

    def shutdown(self):
        self.socket.send(''.encode())
        self.shutdown_request.set()
        self.process.join()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def fwd(self):
        self.command_queue.put('fwd'.encode())

    def bwd(self):
        self.command_queue.put('bwd'.encode())

    def left(self):
        self.command_queue.put('left'.encode())

    def right(self):
        self.command_queue.put('right'.encode())

    def stop(self):
        self.command_queue.put('stop'.encode())


class Server(object):
    def __init__(self, ip, port, handle, name):
        self.ip = ip
        self.port = port
        self.handle = handle
        self.name = name
        self.shutdown_request = Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(0)
        self.connection, addr = self.socket.accept()
        self.process = Process(target=self.handle,
                               name=self.name,
                               args=(self.connection,
                                     self.shutdown_request,
                                     addr))
        self.process.start()
        return self

    def shutdown(self):
        self.shutdown_request.set()
        self.process.join()
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
        except:
            logger.warn(colors.yellow & colors.bold |
                        '{} transport endpoint is not connected.'
                        .format(self.name))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


class Task(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._result = None

    def run(self):
        if self._target is not None:
            self._result = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._result
