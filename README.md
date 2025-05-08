# Sleeping-Detectew
졸음 탐지기

눈을 감은지 3초가 지나면 졸음으로 판단하고 알람을 실행해줌
눈을 감을 때마다 카운트를 해줌

## 목차

1.  [실행하기](#실행하기)
2.  [프로그램 설명](#프로그램-설명)
    1.  [게임 입장 화면](#게임-입장-화면)
    2.  [게임 시작 화면](#게임-시작-화면)
    3.  [주사위 저장 화면](#주사위-저장-화면)
    4.  [다시 굴리기](#다시-굴리기)
3.  [코드 설명](#코드-설명)
4.  [기술 스택](#기술-스택)
5.  [License](#License)
6.  [Reference](#Reference)
7.  [Review](#review)

### 실행하기

---

#### 방법 1: exe 파일 다운로드 후 실행
- 아래 링크에서 파일 다운로드 후 실행  
  [다운로드 링크]

---

#### 방법 2: 파이썬 파일로 실행

##### 1. Python 설치
- Python 3.8 이상 설치: https://www.python.org/

##### 2. 필요한 패키지 설치
아래 명령어를 터미널(cmd)나 VSCode의 터미널에 입력

```bash
pip install opencv-python numpy dlib pygame
```
##### 3. 모델 파일 준비
-shape_predictor_68_face_landmarks.dat 파일을 다운로드 후, Python 파일과 같은 폴더에 넣기기.

다운로드 링크: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

##### 4. 실행
```bash
    python main.py
```
---
### 프로그램 설명
---
#### 1.졸음 탐지
-눈을 3초동안 감고 있으면 졸음으로 판단
#### 2.알람 울리기
-졸음으로 판단 시 알람을 울림
#### 3.눈 감은 수 파악
-눈을 감을 때마다 카운트를 해줌





---




---
### 코드 설명
---

---
### 기술 스택
---


---
### License
    [MIT License](https://github.com/kim001hs/Sleeping-Detecter/blob/main/LICENSE)
---

---
### Reference
---

---
### Review
---