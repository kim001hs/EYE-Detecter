# EYE-Detecter
### 눈 집중도 탐지기
눈을 감은 횟수, 시간을 감지하여 집중도를 확인할 수 있는 프로그램

## 목차

1.  [실행하기](#실행하기)
2.  [프로그램 설명](#프로그램-설명)
    1.  [실행 화면](#실행-화면)
    2.  [측정 버튼](#측정-버튼)
    3.  [확장 화면](#확장-화면)
    4.  [알람 울리기](#알람-울리기)
3.  [코드 설명](#코드-설명)
4.  [기술 스택](#기술-스택)
5.  [License](#License)
6.  [Reference](#Reference)
7.  [Review](#review)



<br>

---

### 실행하기

---

#### 파이썬 파일로 실행
##### 실행환경
    PyQt6==6.9.0
    PyQt6-Qt6==6.9.0
    PyQt6_sip==13.10.0
    opencv-python==4.11.0.86
    dlib==19.22.99-cp310 @ https://github.com/z-mahmud22/Dlib_Windows_Python3.x/blob/main/dlib-19.22.99-cp310-cp310-win_amd64.whl
    pygame==2.6.1
    matplotlib==3.10.3
    numpy==1.26.4

##### 1. Python 설치
- Python 3.8 이상 설치: https://www.python.org/


##### 2. 필요한 패키지 설치
아래 명령어를 터미널(cmd)나 VSCode의 터미널에 입력

```bash
pip install opencv-python numpy dlib pygame PyQt6 matplotlib
```

dlib 설치 실패시 아래 링크로 설치<br>
https://github.com/z-mahmud22/Dlib_Windows_Python3.x/blob/main/dlib-19.22.99-cp310-cp310-win_amd64.whl


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

#### 실행 화면

<br>
<img src="data/default.png" alt="default" width="50%"><br>
기본 실행 시 나오는 화면이다. ?, +, X 버튼은 각각 프로그램 소개, 확장, 닫기 기능을 담당한다.

<br>
<img src="data/q_btn.png" alt="q_btn" width="50%"><br>
? 버튼 위에 마우스를 가져다 대면 다음과 같은 소개가 출력된다.

---

#### 측정 버튼

<br>
<img src="data/default.png" alt="default" width="50%"><br>
연두색 측정시작 버튼을 누르면 기존의 기록을 초기화하고 측정을 시작한다.

<br>
<img src="data/running.png" alt="running" width="50%"><br>
측정 버튼이 클릭되면 버튼은 빨간색 측정종료 버튼으로 바뀐다.
동시에 측정이 시작되며 카메라 프레임마다 얼굴을 감지하여 눈이 감겼는지, 떠졌는지, 감지가 안됐는지를 확인해 측정 시간, 누적 횟수, 누적 시간을 표시한다.
1분마다 최근 1분간의 기록을 배열에 저장하는데 확장 화면에서 나올 히스토그램에 사용된다.

<br>
<img src="data/stop.png" alt="stop" width="50%"><br>
측정 종료를 누르면 측정이 종료되고 측정시작 버튼으로 바뀐다.
다시 시작을 누르면 초기화 후 시작된다.

---

#### 확장 화면

<br>
<img src="data/only_extend.png" alt="extended" width="50%"><br>
확장 시 나오는 화면이다. 기존 화면이 확장되어진 모습으로 아래에 그래프가 생겼다. 또한 - 버튼으로 바뀌는데 누르면 다시 작아진다.

<br>
<img src="data/extended.png" alt="start" width="50%"><br>
측정 확장 시 나오는 화면이다. 히스토그램으로 집중도(Score), 보정 집중도(Fixed_Score)가 나온다.
파란색 집중도(Score)는 얼굴이 감지되지 않은 시간만큼을 제외하고 측정하므로 얼굴이 감지되지 않은 시간이 늘어날수록 낮게 측정된다
하늘색으로 파란색 집중도(Score)위에 표시되는 보정된 집중도(Fixed_Score)는 감지되지 않은 시간을 감지된 시간의 횟수와 시간을 같은 비율로 보냈다고 가정해 보정한 집중도이다. <br>
테스트 결과 평균적으로 1분당 눈을 20번, 2초 감는다. 따라서 이 둘을 같은 비율로 나눠서 점수에 반영했다.<br>
각각의 코드는 다음과 같다
```bash
    score_vals = [(60-g)*10/6-((mc / 20) + (md / 2))*5 for mc, md, g in zip(minute_counts, minute_durations, face_non_durations)]
    fixed_score_vals = [s/(60-g)*60-s for s,g in zip(score_vals, face_non_durations)]
```
그래프는 1분마다 실시간으로 업데이트된다.

<br>
<img src="data/extended_end.png" alt="extended_end" width="50%"><br>
측정을 종료하면 멈춘 그래프를 확인할 수 있다

---

#### 알람 울리기

3초동안 눈을 감고있는 상태가 지속되면 data/alarm.mp3를 실행한다.

---

### 코드 설명

main.py
```bash
    def eye_aspect_ratio(eye):
    eye = np.array(eye)
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)
```
눈을 감았는지를 판별하는 EAR(Eye Aspect Ratio)이다.<br>
눈 주위의 6개의 점을 찍어 상하길이 평균을 좌우길이로 나눠 판정한다.<br>
또한 이후에 왼쪽눈과 오른쪽 눈을 평균을 내 0.2보다 작으면 눈을 감았다고 판정한다.<br>
이 프로젝트에서는 0.2를 기준으로 잡았지만 사람마다 눈의 모양이 다르므로 기준을 변경하면 된다.<br>

```bash
if ear < 0.2:
    if eye_closed_start is None:
        eye_closed_start = time.time()
    elif time.time() - eye_closed_start >= 3:
        if not alarm_playing:
            threading.Thread(target=play_alarm).start()
            alarm_playing = True
```
EAR이 0.2보다 낮은 상태로 3초간 유지되면 알람을 재생한다.<br>
알람이 중복되게 울리지 않게 했다.<br>

```bash
if elapsed_seconds >= next_minute_mark:
    ...
    next_minute_mark += graph_update_time
    self.overlay.update_graph(minute_counts, minute_durations, face_non_durations)
```
카메라가 매우 빠르게 프레임을 처리하기 때문에 1분마다 한 번만 값을 저장 및 그래프 갱신하도록 next_minute_mark 기준을 사용했다.<br>
저장되는 값은 다음과 같다<br>
- 눈 감은 횟수 (minute_counts)
- 감은 시간 (minute_durations)
- 얼굴 미인식 시간 (face_non_durations)

예시: 1분 동안 4번 눈 감고 6.2초 동안 감았으며 1.1초 동안 얼굴이 감지되지 않았으면 해당 값이 리스트에 저장되고 그래프에 업데이트됨


Overlay_Style.py
```bash
def __init__(self):
    self.setWindowOpacity(0.7)
```
투명도이다 0에 가까울수록 투명해지고 1일수록 진해진다. 조정해서 쓸 수 있다

```bash
    score_vals = [(60-g)*10/6-((mc / 20) + (md / 2))*5 for mc, md, g in zip(minute_counts, minute_durations, face_non_durations)]
    fixed_score_vals = [s/(60-g)*60-s for s,g in zip(score_vals, face_non_durations)]
```
위의 코드를 사용해 1분 단위 집중도를 계산하여 시각화했다
- g: 얼굴 미검출 시간
- mc: 눈 감은 횟수
- md: 감은 시간
- s: score(파란색 집중도 그래프)

```bash
def toggle_analysis_mode(self):
    if not self.analysis_mode:
        # 확장: 분석 모드 진입
        ...
        self.setFixedSize(self.analysis_size)
        ...
        self.canvas = FigureCanvas(self.fig)
        ...
        self.layout().insertWidget(2, self.canvas)
        ...
        self.analysis_mode = True
    else:
        # 축소: 기본 모드로 복귀
        ...
        self.setFixedSize(self.default_size)
        ...
        self.analysis_mode = False
```
분석모드, 기본모드를 구성하는 부분이다.
+버튼 클릭 시 창 크기를 키우고 1분 단위 집중도 그래프를 보여준다
-버튼 클릭 시 창 크기를 줄인다

---
### 기술 스택

<img src="https://img.shields.io/badge/Python-색상?style=for-the-badge&logo=python&logoColor=white">


---

### License
[MIT License](https://github.com/kim001hs/Sleeping-Detecter/blob/main/LICENSE)

---

### Reference

Generated in part with the assistance of ChatGPT.

---

### Review

##### ✅ 개발 성과
- 초기에는 단순히 눈 감김을 감지하는 기능만 구현하려 했으나, 이후 반투명 오버레이 UI, 1분 단위 집중도 그래프 등 시각화 기능을 추가하여 사용자 경험을 향상시켰다.
- 기본 모드 / 분석 모드 전환 기능을 통해 평상시에는 미니멀한 인터페이스로 측정에 집중할 수 있고, 필요할 때 분석 데이터를 확인할 수 있도록 설계했다.

---

##### ⚠️ 한계 및 개선 필요 사항
- 얼굴 전체를 인식한 후 눈을 감지하는 방식이기 때문에, 손으로 얼굴 일부를 가리는 경우(예: 턱을 괴는 자세 등) 감지가 어려운 한계가 있다.
- PyInstaller를 사용해 실행 파일로 배포하려 했지만, 라이브러리 의존성 문제로 빌드 오류가 발생해 exe 파일 생성에 실패했다. 여러 방법으로 해결을 시도했지만 끝내 완전한 해결에는 도달하지 못했다.

---

##### 💡 프로젝트를 통해 얻은 점
- Python에 대한 깊은 사전 지식이 없는 상태에서 프로젝트를 시작했지만, 다양한 라이브러리(PyQt6, OpenCV, dlib, matplotlib 등)를 직접 활용하면서 Python 생태계에 대한 이해도를 크게 높일 수 있었다.
- 얼굴 인식 과정에서 68개의 얼굴 랜드마크 포인트를 활용하는 방식을 접하고 이를 기반으로 눈의 상태를 판단하는 로직을 구현한 경험을 토대로 컴퓨터 비전이 실제로 어떻게 활용되는지 알 수 있어서 좋았다

---
