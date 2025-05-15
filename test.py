import cv2
import numpy as np
import dlib
import pygame
import time
import threading
import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore

# PyQt 오버레이 클래스
class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint |
                            QtCore.Qt.WindowType.WindowStaysOnTopHint |
                            QtCore.Qt.WindowType.Tool |
                            QtCore.Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(1600, 30, 300, 100)

        self.label = QtWidgets.QLabel("⏱ 00:00\n👁 0회\n⏳ 0.00s", self)
        self.label.setStyleSheet("color: black; font-size: 18px;")
        self.label.move(0, 0)

    def update_text(self, text):
        self.label.setText(text)

# OpenCV + dlib 감지 루프
def run_cv_loop(overlay):
    eye_closed_start = None
    alarm_playing = False
    eye_closed = False
    eye_closed_count = 0
    eye_closed_time = 0
    start_time = time.time()
    minute_counts = []
    minute_durations = []
    prev_closed_count = 0
    prev_closed_time = 0
    next_minute_mark = 60

    def eye_aspect_ratio(eye):
        eye = np.array(eye)
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)

    def play_alarm():
        pygame.mixer.init()
        pygame.mixer.music.load("data/alarm.mp3")
        pygame.mixer.music.play()

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    (lStart, lEnd) = (42, 48)
    (rStart, rEnd) = (36, 42)

    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("카메라 프레임을 읽을 수 없습니다.")
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            if len(faces) == 0:
                print("얼굴을 찾을 수 없습니다.")
                continue

            for face in faces:
                shape = predictor(gray, face)
                shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

                left_eye = shape[lStart:lEnd]
                right_eye = shape[rStart:rEnd]
                ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
                print(f"EAR: {ear:.2f}")

                if ear < 0.2:
                    if eye_closed_start is None:
                        eye_closed_start = time.time()
                    elif time.time() - eye_closed_start >= 3:
                        print("눈을 감고 있습니다.")
                        if not alarm_playing:
                            threading.Thread(target=play_alarm).start()
                            alarm_playing = True
                    if not eye_closed:
                        eye_closed = True
                        eye_closed_count += 1
                else:
                    if(eye_closed_start is not None):
                        eye_closed_time += time.time() - eye_closed_start
                    eye_closed_start = None
                    eye_closed = False
                    alarm_playing = False

            elapsed_seconds = int(time.time() - start_time)
            if elapsed_seconds >= next_minute_mark:
                current_minute = next_minute_mark // 60
                minute_counts.append(eye_closed_count - prev_closed_count)
                minute_durations.append(eye_closed_time - prev_closed_time)
                prev_closed_count = eye_closed_count
                prev_closed_time = eye_closed_time
                next_minute_mark += 60

            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            overlay_text = f"⏱ {minutes:02}:{seconds:02}\n 👁 {eye_closed_count}회\n ⏳ {eye_closed_time:.2f}s"
            print(overlay_text)
            if overlay:
                overlay.update_text(overlay_text)

            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) == 27:
                break
    finally:
        print(f"눈을 감은 횟수: {eye_closed_count}")
        cap.release()
        cv2.destroyAllWindows()

# 메인 함수에서 PyQt와 OpenCV 실행
def main():
    app = QtWidgets.QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()

    threading.Thread(target=run_cv_loop, args=(overlay,), daemon=True).start()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
