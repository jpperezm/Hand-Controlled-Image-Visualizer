import math

import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

from GUI import *

start: list[int] = [0, 0]
start_length: int = 0
count: int = 0

drag = False
incremented = False
decremented = False
switched_photo = False


def angle_between(p1, p2):          # Calculate the angle between two points
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))


def reset_start():
    global start
    global count
    start = [0, 0]
    count = 0

def watch_for_scale_controls(detected_hands, detector, img):
    lmList1 = detected_hands[0]['lmList']
    lmList2 = detected_hands[1]['lmList']
    global start_length
    if start_length == 0:
        length, info, img = detector.findDistance(lmList1[8][:2], lmList2[8][:2], img)
        start_length = length

    length, info, img = detector.findDistance(lmList1[8][:2], lmList2[8][:2], img)
    angle = math.floor(angle_between(lmList1[8][:2], lmList2[8][:2]))
    scale = length - start_length
    start_length = length
    if (math.floor(scale) > -5) and (math.floor(scale) < 0):
        return 0
    return math.floor(scale)


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()

    cap = cv2.VideoCapture(0)
    cap.set(3, 800)
    cap.set(4, 800)
    global start_length
    global drag

    last_hand_pos = None

    detector = HandDetector(detectionCon=0.8)

    while True:
        success, img = cap.read()

        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        
        hands, img = detector.findHands(img)
        img = cv2.flip(img, 1)
        if len(hands) == 1:
            if detector.fingersUp(hands[0]) == [1, 1, 1, 0, 0] and hands[0]['type'] == 'Left':
                print("next")
                if not switched_photo:
                    switched_photo = True
                    window.showNextImage()
            elif detector.fingersUp(hands[0]) == [1, 1, 1, 0, 0] and hands[0]['type'] == 'Right':
                print("previous")
                if not switched_photo:
                    switched_photo = True
                    window.showPreviousImage()
            elif detector.fingersUp(hands[0]) == [0, 0, 0, 0, 0]:
                reset_start();
                start_length = 0
                switched_photo = False

        elif len(hands) == 2:
            if detector.fingersUp(hands[0]) == [1, 1, 0, 0, 0] and detector.fingersUp(hands[1]) == [1, 1, 0, 0, 0]:   # ZOOM
                window.viewer.changeZoom(watch_for_scale_controls(hands, detector, img))
            elif (detector.fingersUp(hands[0]) == [1, 1, 1, 1, 1] and detector.fingersUp(hands[1]) == [1, 1, 0, 0, 0]) or (detector.fingersUp(hands[1]) == [1, 1, 1, 1, 1] and detector.fingersUp(hands[0]) == [1, 1, 0, 0, 0]):   # DRAG
                current_hand_pos = np.array(hands[0]['lmList'][0][:2])  # Position of the wrist as reference
                if last_hand_pos is not None:
                    move = current_hand_pos - last_hand_pos
                    window.viewer.dragImage(QtCore.QPointF(move[0], move[1]))
                last_hand_pos = current_hand_pos
            else:
                reset_start();
                start_length = 0
                switched_photo = False
                last_hand_pos = None
        else:
            reset_start();
            start_length = 0
            switched_photo = False

        img = cv2.flip(img, 1)
        cv2.imshow('Hand Gesture Recognition', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main()
