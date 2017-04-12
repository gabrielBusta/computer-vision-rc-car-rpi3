import datetime
import cv2
import numpy as np
from multiprocessing import Process, Event


def GaussianBlur(frame, kernelSize=(5, 5), sigma=0):
    return cv2.GaussianBlur(frame, kernelSize, sigma)


def GrayScale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def InvertedBinaryThreshold(frame, lowerBound, upperBound):
    ret, thresholded = cv2.threshold(frame, lowerBound, upperBound,
                                     cv2.THRESH_BINARY_INV)
    return thresholded


class VisionManager(object):
    def __init__(self, shape, stopSignClassifier, speedSignClassifier):
        self.height, self.width, self.channels = shape
        self.stopSignClassifier = stopSignClassifier
        self.speedSignClassifier = speedSignClassifier
        # Classifier parameters.
        self.stopSignScaleFactor = 1.3
        self.stopSignMinNeighbors = 5
        self.speedSignScaleFactor = 1.3
        self.speedSignMinNeighbors = 5
        # We will include the frame up to a horizontal line
        # going through this x coordinate.
        self.laneROIUpperBound = 390
        # Visualization Parameters.
        self.lineThickness = 3
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontThickness = 1
        self.fontScale = 1
        self.BLUE = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (0, 0, 255)

    def detectLanes(self, frame):
        roi = frame[self.laneROIUpperBound:self.height, 0:self.width]
        roi_canny = cv2.Canny(frame, 90, 200)
        lanes = cv2.HoughLinesP(roi_canny,
                            1,
                            np.pi / 180,
                            30,
                            np.array([]),
                            minLineLength=20,
                            maxLineGap=20)
        return lanes

    def detectSpeedSigns(self, frame):
        # TODO: Make it pick the biggest speed sign in sight.
        return self.speedSignClassifier.detectMultiScale(frame, self.speedSignScaleFactor,
                                                         self.speedSignMinNeighbors)

    def detectStopSigns(self, frame):
        # TODO: Make it pick the biggest stop sign in sight.
        return self.stopSignClassifier.detectMultiScale(frame, self.stopSignScaleFactor,
                                                        self.stopSignMinNeighbors)

    def drawLanes(self, frame, lanes):
        if lanes is not None:
            for lane in lanes:
                for x1, y1, x2, y2 in lane:
                    cv2.line(frame,
                             (x1, y1 + self.laneROIUpperBound),
                             (x2, y2 + self.laneROIUpperBound),
                             self.BLUE,
                             self.lineThickness)

    def drawSpeedSigns(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h), self.GREEN, self.lineThickness)
            cv2.putText(frame, 'Speed Limit', (x, y - 8), self.font,
                        1, self.GREEN, self.fontWeight, cv2.LINE_AA)

    def drawStopSigns(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h), self.RED, self.lineThickness)
            cv2.putText(frame, 'Speed Limit', (x, y - 8), self.font, self.fontScale,
                        self.RED, self.fontThickness, cv2.LINE_AA)

    def readDigits(self, frame, signs):
        for x, y, w, h in signs:
            roi = frame[y:y+h, x:x+w]
            return roi
        return np.zeros((self.height, self.width, self.channels))


class FPSTimer(object):
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.numFrames = 0

    def start(self):
        self.startTime = datetime.datetime.now()
        return self

    def stop(self):
        self.endTime = datetime.datetime.now()

    def update(self):
        self.numFrames += 1

    def elapsed(self):
        return (self.endTime - self.startTime).total_seconds()

    def fps(self):
        return self.numFrames / self.elapsed()


class VideoStream(object):
    def __init__(self, url):
        self.stream = cv2.VideoCapture(url)
        self.streaming, self.frame = self.stream.read()
        self.shutdownRequest = Event()

    def start(self):
        self.process = Process(target=self.update, args=(self.shutdownRequest))
        self.process.start()
        return self

    def update(self, shutdownRequest):
        while not shutdownRequest.is_set():
            self.streaming, self.frame = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.shutdownRequest.set()
        self.process.join()
        self.stream.release()
