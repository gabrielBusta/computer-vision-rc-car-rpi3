import cv2
import socket
from time import sleep
from settings import *


def main():
    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote.connect((ROBOT_IP, REMOTE_CONTROL_PORT))
    print('ok')

    distance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    distance.connect((ROBOT_IP, ULTRASONIC_SENSOR_PORT))
    print('ok')

    cv2.namedWindow(ROBOT_IP, cv2.WINDOW_AUTOSIZE)
    video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    print('ok')
    try:
        streaming, frame = video.read()
        print(streaming)
        while streaming:
            print(streaming)
            print(frame)
            cv2.imshow(ROBOT_IP, frame)
            streaming, frame = video.read()
    finally:
        video.release()
        remote.shutdown(socket.SHUT_RDWR)
        remote.close()
        distance.shutdown(socket.SHUT_RDWR)
        distance.close()


if __name__ == "__main__":
    main()
