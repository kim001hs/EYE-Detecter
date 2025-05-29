from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
matplotlib.rcParams['font.family'] = 'Arial'   # Arial 등 영어 기본 폰트 사용

class Overlay_Style(QtWidgets.QWidget):
    measure_signal = QtCore.pyqtSignal(bool)  # True: 측정 시작, False: 측정 종료

    def __init__(self):
        super().__init__()
        # --- 상태 변수 ---
        self.is_measuring = False
        self.analysis_mode = False
        self._drag_pos = None
        self._default_pos = None
        self.default_size = QtCore.QSize(320, 180)
        self.analysis_size = QtCore.QSize(600, 400)
        self.setWindowOpacity(0.7)

        # --- UI 생성 ---
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.default_size)

        # 상단바
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
        
        help_tooltip = "이 프로그램은 눈의 감김을 감지하여 깜빡임 횟수, 감긴 시간을 측정합니다."
        "\n+ 버튼을 눌러 측정한 결과를 바탕으로한 집중도 분석 페이지를 볼 수 있습니다"
        "\n측정 시작/종료 버튼을 눌러 측정을 시작하거나 종료할 수 있습니다."
        "\n측정 중에는 측정 시간, 누적 횟수, 누적 시간을 실시간으로 확인할 수 있습니다."
        "\n집중도 "
        q_btn = QtWidgets.QToolButton(self)
        q_btn.setText("?")
        q_btn.setToolTip(help_tooltip)
        q_btn.setStyleSheet(" color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        self.plus_btn = QtWidgets.QToolButton(self)
        self.plus_btn.setText("+")
        self.plus_btn.setStyleSheet("background: #a9e736; color: #494; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        self.plus_btn.clicked.connect(self.toggle_analysis_mode)
        close_btn = QtWidgets.QToolButton(self)
        close_btn.setText("✕")
        close_btn.setStyleSheet("background: #ff5555; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        close_btn.clicked.connect(QtWidgets.QApplication.quit)
        title_layout.addWidget(q_btn)
        title_layout.addWidget(self.plus_btn)
        title_layout.addWidget(close_btn)

        # --- 상단 통계 영역 ---
        stats_widget = QtWidgets.QWidget(self)
        stats_layout = QtWidgets.QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(20, 12, 20, 0)
        stats_layout.setSpacing(36)

        label_names = ["측정 시간", "누적 횟수", "누적 시간"]
        label_values = ["00:00", "0", "0"]
        value_colors = ["#ffe400", "#b8ff53", "#ffe400"]
        self.value_labels = []

        for name, val, vcolor in zip(label_names, label_values, value_colors):
            col_widget = QtWidgets.QWidget()
            col_layout = QtWidgets.QVBoxLayout(col_widget)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(2)
            l = QtWidgets.QLabel(name)
            l.setStyleSheet("color: white; font-size: 14px;")
            v = QtWidgets.QLabel(val)
            v.setStyleSheet(f"color: {vcolor}; font-size: 16px; font-weight: bold;")
            v.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.value_labels.append(v)
            col_layout.addWidget(l)
            col_layout.addWidget(v)
            stats_layout.addWidget(col_widget)

        # --- matplotlib 그래프 영역 ---
        self.fig, self.ax = plt.subplots(figsize=(5, 2.2))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background: transparent;")
        self.canvas.hide()  # 기본 상태에서 숨김

        # --- 하단 버튼 ---
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

        # --- 전체 레이아웃 ---
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(title_bar)
        main_layout.addWidget(stats_widget)
        main_layout.addWidget(self.canvas)
        main_layout.addStretch(1)
        main_layout.addWidget(self.start_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_layout.addSpacing(8)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        painter.setBrush(QtGui.QColor(42, 44, 54, 245))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)
        grad_rect = QtCore.QRectF(0, rect.height()-30, rect.width(), 30)
        grad = QtGui.QLinearGradient(0, rect.height()-30, 0, rect.height())
        grad.setColorAt(0, QtGui.QColor(200, 255, 160, 30))
        grad.setColorAt(1, QtGui.QColor(220, 240, 160, 20))
        painter.setBrush(grad)
        painter.drawRoundedRect(grad_rect, 8, 8)

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
            # --- 확장 ---
            self._default_pos = self.pos()
            dx = self.analysis_size.width() - self.default_size.width()
            self.move(self._default_pos.x() - dx, self._default_pos.y())
            self.setFixedSize(self.analysis_size)
            # --- 캔버스 새로 생성 ---
            if hasattr(self, 'canvas') and self.canvas:
                self.layout().removeWidget(self.canvas)
                self.canvas.deleteLater()
            self.fig, self.ax = plt.subplots(figsize=(5, 2.2))
            self.canvas = FigureCanvas(self.fig)
            self.canvas.setStyleSheet("background: transparent;")
            self.layout().insertWidget(2, self.canvas)  # stats_widget 다음에 끼워넣음 (위에서 main_layout.addWidget(self.canvas))
            # self.canvas.show()
            self.analysis_mode = True
            # 최신 그래프 데이터가 있으면 즉시 그림
            if hasattr(self, 'graph_data_tuple'):
                self.update_graph(*self.graph_data_tuple)
        else:
            # --- 축소 ---
            if hasattr(self, 'canvas') and self.canvas:
                self.layout().removeWidget(self.canvas)
                self.canvas.deleteLater()
                self.canvas = None
            if self._default_pos is not None:
                self.move(self._default_pos)
            self.setFixedSize(self.default_size)
            self.analysis_mode = False

    def update_graph(self, minute_counts, minute_durations, face_non_durations):
        if not hasattr(self, "canvas") or self.canvas is None or not self.isVisible():
            return
        import matplotlib
        matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Liberation Sans', 'sans-serif']

        self.graph_data_tuple = (minute_counts, minute_durations, face_non_durations)
        if not hasattr(self, 'ax') or self.ax is None:
            return
        self.ax.clear()

        n = len(minute_counts)
        x = np.arange(0,n)
        # 미검출 시간을 0~100 스케일로 변환
        gray_vals = [fnd*10/6 for fnd in face_non_durations]
        score_vals = [100 - g*10/6 - ((mc / 20) + (md / 2)) * 10 / 3     for mc, md, g in zip(minute_counts, minute_durations, gray_vals)]
        
        # 점수와 회색 합이 100을 넘지 않도록 클리핑
        score_vals = [min(y, 100) for y in score_vals]
        gray_vals = [min(g, 100-s) for g, s in zip(gray_vals, score_vals)]  # 초록 위에 덮을 수 있는 만큼만 회색

        width = 1.0

        # 초록 bar
        self.ax.bar(x, score_vals, width=width, color="#4774cf", label='Score', zorder=2)
        # 회색 bar, 초록 위에 bottom=score_vals로 쌓기!
        self.ax.bar(x, gray_vals, width=width, color='gray', alpha=0.5, bottom=score_vals, label='None time (gray)', zorder=1)

        # x축 중앙에 분 표시
        self.ax.set_xticks(x + 0.5)
        self.ax.set_xticklabels([str(i+1) for i in range(n)])
        self.ax.set_xlim(0, n)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Minute")
        self.ax.set_ylabel("concentration")            
        self.ax.set_title("Concentration (per Minute)")
        self.ax.legend()
        self.fig.tight_layout()
        self.canvas.draw()



    def update_values(self, time_str, count, duration):
        self.value_labels[0].setText(time_str)
        self.value_labels[1].setText(str(count))
        self.value_labels[2].setText(f"{duration:.2f}")

    # 드래그 이동
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
    def mouseReleaseEvent(self, event):
        self._drag_pos = None
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            QtWidgets.QApplication.quit()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Overlay_Style()
    win.show()

    # 테스트: 임시 데이터로 그래프 업데이트
    import random
    from PyQt6.QtCore import QTimer
    minute_counts = []
    minute_durations = []
    face_non_durations = []
    def test_graph_update():
        minute_counts.append(random.randint(0, 10))
        minute_durations.append(random.uniform(0, 5))
        face_non_durations.append(random.uniform(0, 2))
        if win.analysis_mode:
            win.update_graph(minute_counts, minute_durations, face_non_durations)
    timer = QTimer()
    timer.timeout.connect(test_graph_update)
    timer.start(60000)  # 1분마다 (테스트용 1초로 바꿔도 됨)
    sys.exit(app.exec())
