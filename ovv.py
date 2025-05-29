from PyQt6 import QtWidgets, QtCore, QtGui

class Overlay_Style(QtWidgets.QWidget):
    measure_signal = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.default_size = QtCore.QSize(320, 180)
        self.analysis_size = QtCore.QSize(600, 400)
        self.is_measuring = False
        self.analysis_mode = False  # 분석모드 여부
        self.init_ui()
        self._drag_pos = None
        self.setWindowOpacity(0.7)

    def init_ui(self):
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(320, 180)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 상단 바
        title_bar = QtWidgets.QWidget(self)
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("""
            background-color: #2b2b2b;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(14, 0, 8, 0)
        title_label = QtWidgets.QLabel("EYE DETECTER", self)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 15px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        # 도움말, +, 닫기 버튼
        q_btn = QtWidgets.QToolButton(self)
        q_btn.setText("?")
        q_btn.setToolTip("이 프로그램은 눈의 감김을 감지하여 깜빡임 횟수, 감긴 시간을 측정합니다.")
        q_btn.setStyleSheet("background: #fff3; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        plus_btn = QtWidgets.QToolButton(self)
        plus_btn.setText("+")
        plus_btn.setStyleSheet("background: #a9e736; color: #494; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        plus_btn.clicked.connect(self.toggle_analysis_mode)
        close_btn = QtWidgets.QToolButton(self)
        close_btn.setText("✕")
        close_btn.setStyleSheet("background: #ff5555; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        close_btn.clicked.connect(QtWidgets.QApplication.quit)
        title_layout.addWidget(q_btn)
        title_layout.addWidget(plus_btn)
        title_layout.addWidget(close_btn)

        # 측정 라벨
        center = QtWidgets.QWidget(self)
        center.setStyleSheet("background: transparent;")
        center_layout = QtWidgets.QGridLayout(center)
        center_layout.setContentsMargins(24, 6, 24, 6)
        center_layout.setVerticalSpacing(8)
        label_names = ["측정 시간", "누적 횟수", "누적 시간"]
        label_values = ["00:00", "0", "0"]
        value_colors = ["#ffe400", "#b8ff53", "#ffe400"]
        self.value_labels = []
        for row, (name, val, vcolor) in enumerate(zip(label_names, label_values, value_colors)):
            l = QtWidgets.QLabel(name)
            l.setStyleSheet("color: white; font-size: 14px;")
            v = QtWidgets.QLabel(val)
            v.setStyleSheet(f"color: {vcolor}; font-size: 14px; font-weight: bold;")
            self.value_labels.append(v)
            center_layout.addWidget(l, row, 0, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
            center_layout.addWidget(v, row, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        # 하단 버튼
        self.start_btn = QtWidgets.QPushButton("측정시작", self)
        self.start_btn.setFixedHeight(38)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #a9e736;
                color: #364914;
                font-size: 17px;
                border-radius: 10px;
                font-weight: bold;
                border: 2px solid #7db53a;
            }
            QPushButton:hover { background-color: #b8ff53; }
        """)
        self.start_btn.clicked.connect(self.toggle_measure)

        # 분석 결과(분석모드에만 표시)
        self.analysis_label = QtWidgets.QLabel("여기에 분석 결과가 표시됩니다.", self)
        self.analysis_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.analysis_label.setStyleSheet("color: black; font-size: 17px;")
        self.analysis_label.setVisible(False)  # 평소엔 숨김

        # 레이아웃 배치
        main_layout.addWidget(title_bar)
        main_layout.addWidget(center)
        main_layout.addStretch(1)
        main_layout.addWidget(self.analysis_label)
        main_layout.addWidget(self.start_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_layout.addSpacing(8)

    def toggle_measure(self):
        if not self.is_measuring:
            self.is_measuring = True
            self.start_btn.setText("측정종료")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff5555;
                    color: white;
                    font-size: 17px;
                    border-radius: 10px;
                    font-weight: bold;
                    border: 2px solid #a33;
                }
                QPushButton:hover { background-color: #ff7575; }
            """)
            self.measure_signal.emit(True)
        else:
            self.is_measuring = False
            self.start_btn.setText("측정시작")
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a9e736;
                    color: #364914;
                    font-size: 17px;
                    border-radius: 10px;
                    font-weight: bold;
                    border: 2px solid #7db53a;
                }
                QPushButton:hover { background-color: #b8ff53; }
            """)
            self.measure_signal.emit(False)

    def toggle_analysis_mode(self):
        if not self.analysis_mode:
            self.setFixedSize(600, 400)
            # 확장 전 위치 저장
            self._default_pos = self.pos()
            # 창을 왼쪽(폭 증가분만큼), 아래로 확장
            dx = self.analysis_size.width() - self.default_size.width()
            dy = self.analysis_size.height() - self.default_size.height()
            new_x = self._default_pos.x() - dx
            new_y = self._default_pos.y()
            self.setGeometry(new_x, new_y, self.analysis_size.width(), self.analysis_size.height())
            self.analysis_label.setVisible(True)
            self.analysis_label.setText("여기에 분석 결과가 표시됩니다.\n(측정 기록이나 그래프, 집중도 등...)")
            self.analysis_mode = True
        else:
            self.setFixedSize(320, 180)
            # 원래 위치/크기로 복귀
            if self._default_pos is not None:
                self.setGeometry(self._default_pos.x(), self._default_pos.y(), self.default_size.width(), self.default_size.height())
            else:
                self.setFixedSize(self.default_size)
            self.analysis_label.setVisible(False)
            self.analysis_mode = False
            
    def update_values(self, time_str, count, duration):
        self.value_labels[0].setText(time_str)
        self.value_labels[1].setText(str(count))
        self.value_labels[2].setText(f"{duration:.2f}")
