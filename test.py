import cv2
import numpy as np
import dlib
import pygame
import time
import threading
import sys
from PyQt6 import QtWidgets
from test_overlay2 import Overlay_Style

class CVWorker:
    def __init__(self, overlay):
        self.overlay = overlay
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_cv_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def run_cv_loop(self):
        eye_closed_start = None
        face_none_start = None
        alarm_playing = False
        eye_closed = False
        eye_closed_count = 0
        eye_closed_time = 0
        face_none_time = 0
        start_time = None
        minute_counts = []
        minute_durations = []
        face_non_durations = []
        prev_closed_count = 0
        prev_closed_time = 0
        prev_none_time = 0
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
            while self.running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("카메라 프레임을 읽을 수 없습니다.")
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)
                if start_time is None:
                    start_time = time.time()
                elapsed_seconds = int(time.time() - start_time)
                
                minutes = elapsed_seconds // 60
                seconds = elapsed_seconds % 60
                if elapsed_seconds >= next_minute_mark:
                    if eye_closed_start is not None:
                        eye_closed_time += time.time() - eye_closed_start
                        eye_closed_start = None
                    if face_none_start is not None:
                        face_none_time += time.time() - face_none_start
                        face_none_start = None
                    minute_counts.append(eye_closed_count - prev_closed_count)
                    print(f"1분동안 눈 감은 수: {eye_closed_count - prev_closed_count}")
                    minute_durations.append(eye_closed_time - prev_closed_time)
                    print(f"1분동안 눈 감은 시간: {eye_closed_time - prev_closed_time}")
                    face_non_durations.append(face_none_time - prev_none_time)
                    print(f"1분동안 얼굴 인식이 되지 않은 시간: {face_none_time - prev_none_time}")
                    prev_closed_count = eye_closed_count
                    prev_closed_time = eye_closed_time
                    prev_none_time = face_none_time
                    next_minute_mark += 60
                    self.overlay.update_graph(minute_counts, minute_durations, face_non_durations)
                
                if len(faces) == 0:
                    if eye_closed_start is not None:
                        eye_closed_time += time.time() - eye_closed_start
                        eye_closed_start = None
                    if face_none_start is None:
                        face_none_start = time.time()
                    # print("얼굴을 찾을 수 없습니다.")
                    self.overlay.update_values(f"{minutes:02}:{seconds:02}", eye_closed_count, eye_closed_time)
                    continue
                else:
                    if face_none_start is not None:
                        face_none_time += time.time() - face_none_start
                        face_none_start = None
                    
                for face in faces:
                    shape = predictor(gray, face)
                    shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

                    left_eye = shape[lStart:lEnd]
                    right_eye = shape[rStart:rEnd]
                    ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
                    # print(f"EAR: {ear:.2f}")

                    if ear < 0.2:
                        if eye_closed_start is None:
                            eye_closed_start = time.time()
                        elif time.time() - eye_closed_start >= 3:
                            # print("눈을 감고 있습니다.")
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

                if self.overlay:
                    self.overlay.update_values(f"{minutes:02}:{seconds:02}", eye_closed_count, eye_closed_time)
                # cv2.imshow("Frame", frame)
                # if cv2.waitKey(1) == 27:
                #     break
        finally:
            print(f"눈을 감은 횟수: {eye_closed_count}")
            cap.release()
            cv2.destroyAllWindows()

def main():
    app = QtWidgets.QApplication(sys.argv)
    overlay = Overlay_Style()
    overlay.show()

    worker = CVWorker(overlay)
    overlay.measure_signal.connect(lambda start: worker.start() if start else worker.stop())

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
