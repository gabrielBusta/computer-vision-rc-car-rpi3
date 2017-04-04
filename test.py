import cv2
import socket
import time
import sys
from settings import *


def main():
    if REMOTE_CONTROL_ON:
        sys.stdout.write('Testing remote control... ')
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((ROBOT_IP, REMOTE_CONTROL_PORT))
        remote.send('fwd'.encode())
        time.sleep(1)
        remote.send('bwd'.encode())
        time.sleep(1)
        remote.send('left'.encode())
        time.sleep(1)
        remote.send('right'.encode())
        time.sleep(1)
        remote.send('stop'.encode())
        remote.shutdown(socket.SHUT_RDWR)
        remote.close()
        sys.stdout.write('ok\n')

    if ULTRASONIC_SENSOR_ON:
        sys.stdout.write('Testing ultrasonic sensor... ')
        ultrasonic_sensor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ultrasonic_sensor.connect((ROBOT_IP, ULTRASONIC_SENSOR_PORT))
        distance = ultrasonic_sensor.recv(1024).decode()
        while not distance:
            distance = ultrasonic_sensor.recv(1024).decode()
        if distance:
            sys.stdout.write('ok\n')
        ultrasonic_sensor.shutdown(socket.SHUT_RDWR)
        ultrasonic_sensor.close()

    if CAMERA_ON:
        sys.stdout.write('Testing camera... ')
        video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
        streaming, frame = video.read()
        if streaming:
            sys.stdout.write('ok\n')
        video.release()


if __name__ == "__main__":
    main()
