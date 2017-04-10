import cv2
import numpy as np


def GaussianBlur(frame, kernelSize=(5, 5), sigma=0):
    return cv2.GaussianBlur(frame, kernelSize, sigma)


def GrayScale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def InvertedBinaryThreshold(frame, lowerBound, upperBound):
    ret, thresholded = cv2.threshold(frame, lowerBound, upperBound, cv2.THRESH_BINARY_INV)
    return thresholded


class CVManager(object):
    def __init__(self, shape, stopSignClassifier, speedSignClassifier):
        self.height, self.width, self.channels = shape
        self.stopSignClassifier = stopSignClassifier
        self.speedSignClassifier = speedSignClassifier

        self.stopSignScaleFactor = 1.3
        self.stopSignMinNeighbors = 5
        self.speedSignScaleFactor = 1.3
        self.speedSignMinNeighbors = 5
        self.laneROIUpperBound = 390

        self.lineThickness = 3
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontWeight = 1
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
        return self.speedSignClassifier.detectMultiScale(frame, self.speedSignScaleFactor, self.speedSignMinNeighbors)

    def detectStopSigns(self, frame):
        # TODO: Make it pick the biggest stop sign in sight.
        return self.stopSignClassifier.detectMultiScale(frame, self.stopSignScaleFactor, self.stopSignMinNeighbors)

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
            cv2.putText(frame, 'Speed Limit', (x, y - 8), self.font, 1, self.GREEN, self.fontWeight, cv2.LINE_AA)

    def drawStopSigns(self, frame, signs):
        for x, y, w, h in signs:
            cv2.rectangle(frame, (x, y), (x + w, y + h), self.RED, self.lineThickness)
            cv2.putText(frame, 'Speed Limit', (x, y - 8), self.font, 1, self.RED, self.fontWeight, cv2.LINE_AA)

    def readDigits(self, frame, signs):
        for x, y, w, h in signs:
            roi = frame[y:y+h, x:x+w]
            return roi
        return np.zeros((self.height, self.width, self.channels))
