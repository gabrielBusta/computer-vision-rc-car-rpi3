import socket
from threading import Thread
from multiprocessing import Process, Queue, Event, queues


class RemoteControl(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commandQueue = Queue()
        self.shutdownRequest = Event()

    def start(self):
        self.socket.connect((self.ip, self.port))
        self.process = Process(target=self.sendCommands,
                               daemon=True)
        self.process.start()
        return self

    def sendCommands(self):
        while not self.shutdownRequest.is_set():
            try:
                command = self.commandQueue.get(timeout=0.5)
                self.socket.send(command)
            except queues.Empty:
                continue

    def shutdown(self):
        self.shutdownRequest.set()
        self.process.join()
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def fwd(self):
        self.commandQueue.put('fwd'.encode())

    def bwd(self):
        self.commandQueue.put('bwd'.encode())

    def left(self):
        self.commandQueue.put('left'.encode())

    def right(self):
        self.commandQueue.put('right'.encode())

    def stop(self):
        self.commandQueue.put('stop'.encode())


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
        return self

    def shutdown(self):
        self.shutdownRequest.set()
        self.process.join()
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
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
