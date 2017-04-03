import cv2
import socket
from settings import *
from multiprocessing import Queue


def main():
    workers = []

    frames = Queue()
    workers.append(Process(target=get_frames,
                           name='CameraStream',
                           args=((ROBOT_IP, CAMERA_PORT), frames)))

    distances = Queue()
    workers.append(Process(target=get_distances,
                           name='UltrasonicSensorStream',
                           args=((ROBOT_IP, ULTRASONIC_SENSOR_PORT), distances)))

    for worker in workers:
        worker.start()


def get_distances(address, distances):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect(address)
    try:
        while True:
            distance = connection.recv(1024)
            distances.put(int(distance))
    finally:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()


def get_frames(address, frames):
    video = cv2.VideoCapture('tcp://{}:{}'.format(ROBOT_IP, CAMERA_PORT))
    try:
        streaming, frame = video.read()
        while streaming:
            frames.put(frame)
            streaming, frame = video.read()
    finally:
        video.release()


if __name__ == "__main__":
    main()
