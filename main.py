import cv2
import numpy as np
import dlib
import pygame
import time
import threading

# 눈을 감았는지 확인하는 함수
# 눈의 세로길이 평균/가로길이 비율을 계산해서 눈을 감았는지 확인(0.2 이하면 눈을 감았다고 판단할 예정정)
def eye_aspect_ratio(eye):
    eye = np.array(eye)  # eye를 numpy 배열로 변환
    # 눈의 세 점을 이용해서 비율 계산
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# 얼굴 탐색해서 위치 잡아주는 함수
detector = dlib.get_frontal_face_detector()
# 얼굴 68개 좌표 잡아주는 함수
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# 오른쪽 눈눈
(lStart, lEnd) = (42, 48)  
# 왼쪽 눈
(rStart, rEnd) = (36, 42)  

# 카메라 열기기
cap= cv2.VideoCapture(0) 
# 눈이 감긴 시점
eye_closed_start = None
# 알람 실행
alarm_playing = False

# 알람
def play_alarm():
    pygame.mixer.init()
    pygame.mixer.music.load("data/alarm.mp3")
    pygame.mixer.music.play()

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("카메라 프레임을 읽을 수 없습니다.")
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.array(gray, dtype=np.uint8)  # 타입을 명확히 설정
    if gray.dtype != np.uint8:
        print("gray가 uint8이 아닙니다.")
    if len(gray.shape) != 2:
        print("gray가 단일 채널 이미지가 아닙니다.")

    faces = detector(gray)
    if len(faces) == 0:
        print("얼굴을 찾을 수 없습니다.")
        continue
    for face in faces:
        shape = predictor(gray, face)
        shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

        left_eye = shape[lStart:lEnd]
        right_eye = shape[rStart:rEnd]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        print(f"EAR: {ear:.2f}")
        if ear < 0.2:
            if eye_closed_start is None:
                eye_closed_start = time.time()
            elif time.time() - eye_closed_start >= 3:
                if not alarm_playing:
                    threading.Thread(target=play_alarm).start()
        else:
            eye_closed_start = None

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == 27:  # ESC 키 누르면 종료
        break

cap.release()
cv2.destroyAllWindows()
