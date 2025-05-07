import os
import random
import cv2 as cv
import numpy as np
import dlib
import sys
from math import atan2, degrees

# 얼굴 탐색해서 위치 잡아주는 함수
detector = dlib.get_frontal_face_detector()
# 얼굴 68개 좌표 잡아주는 함수
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

def get_image_path(folder_path):
    # 이미지 경로
    folder_path = 'data/default'
    # 이미지 파일 파일명 기준 정렬 -> 안하면 랜덤으로 섞임
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jpg')])
    # 이미지 파일 개수
    img_num = len(image_files)
    if img_num == 0:
        print("폴더에 이미지가 없습니다.")
    else:
        # 1부터 img_num 사이의 무작위 자연수 k
        k = random.randint(1, img_num)
        
        # k번째 이미지 선택 (리스트는 0-indexed라서 k-1)
        selected_image = image_files[k - 1]

        # 전체 경로로 이미지 불러오기
        img_path = os.path.join(folder_path, selected_image)
        img = cv.imread(img_path)
def img_transform(img):
    # 이미지 크기 조정
    img = cv.resize(img, (640, 480))
    face=detector(img)
    
    dlib_shape = predictor(img, face)
    shape_2d = np.array([[p.x,p.y] for p in dlib_shape.parts()])

    top_left = np.min(shape_2d, axis=0)
    bottom_right = np.max(shape_2d,axis=0)

    center_X, center_Y = np.mean(shape_2d, axis=0).astype(np.int)
    return img