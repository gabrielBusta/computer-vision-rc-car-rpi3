import socket

class RemoteController(object):
    def __init__(self, address):
        self.address = address
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.clientSocket.connect(self.address)

    def close(self):
        self.clientSocket.shutdown(socket.SHUT_RDWR)
        self.clientSocket.close()

    def fwd(self):
        self.clientSocket.send('fwd'.encode())

    def bwd(self):
        self.clientSocket.send('bwd'.encode())

    def left(self):
        self.clientSocket.send('left'.encode())

    def right(self):
        self.clientSocket.send('right'.encode())

    def stop(self):
        self.clientSocket.send('stop'.encode())


