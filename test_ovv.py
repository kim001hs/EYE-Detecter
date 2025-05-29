from PyQt6 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

class ResultWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("집중도 분석 결과")
        self.resize(600, 400)
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("여기에 분석 결과가 표시됩니다.", self)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
class Overlay_Style(QtWidgets.QWidget):
    measure_signal = QtCore.pyqtSignal(bool)   # 시그널 선언    
    def __init__(self):
        super().__init__()
        self.setWindowOpacity(0.7)
        self._drag_pos = None
        self.extend_window = None
        self.init_ui()

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

    def init_ui(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(320, 180)

        # ---- 상단 바 ----
        title_bar = QtWidgets.QWidget(self)
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("background-color: #2b2b2b; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(14, 0, 8, 0)
        title_label = QtWidgets.QLabel("BATTLE STATISTICS", self)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 15px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)

        # ? 버튼
        q_btn = QtWidgets.QToolButton(self)
        q_btn.setText("?")
        q_btn.setToolTip("도움말을 확인할 수 있습니다.")
        q_btn.setStyleSheet("background: #fff3; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        title_layout.addWidget(q_btn)

        # + 버튼
        self.plus_btn = QtWidgets.QToolButton(self)
        self.plus_btn.setText("+")
        self.plus_btn.setStyleSheet("background: #a9e736; color: #494; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        self.plus_btn.setToolTip("그래프 창 확장")
        self.plus_btn.clicked.connect(self.show_extend)
        title_layout.addWidget(self.plus_btn)
        self.result_window = None
        self.plus_btn.clicked.connect(self.show_result_window)
        
        # X 버튼
        close_btn = QtWidgets.QToolButton(self)
        close_btn.setText("✕")
        close_btn.setToolTip("창을 닫고 프로그램을 종료합니다")
        close_btn.setStyleSheet("background: #ff5555; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        close_btn.clicked.connect(QtWidgets.QApplication.quit)
        title_layout.addWidget(close_btn)

        # ---- 중앙 내용 ----
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

        # ---- 하단 버튼 ----
        start_btn = QtWidgets.QPushButton("측정시작", self)
        start_btn.setFixedHeight(38)
        start_btn.setStyleSheet("""
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
        icon = QtGui.QPixmap(20, 20)
        icon.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(icon)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor("#7db53a"), 3))
        painter.drawEllipse(2, 2, 16, 16)
        painter.drawLine(10, 10, 10, 6)
        painter.drawLine(10, 10, 14, 14)
        painter.end()
        start_btn.setIcon(QtGui.QIcon(icon))
        start_btn.setIconSize(QtCore.QSize(20,20))

        # ---- 전체 레이아웃 ----
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(title_bar)
        main_layout.addWidget(center)
        main_layout.addStretch(1)
        main_layout.addWidget(start_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_layout.addSpacing(8)

    def show_extend(self):
        # 예시 데이터, 실제로는 집계해서 넘기면 됨!
        minute_counts = [4, 8, 2, 3, 5, 1, 6]
        minute_durations = [5, 7, 3, 2, 4, 2, 9]
        face_non_durations = [20, 0, 10, 5, 0, 0, 15]

        if self.extend_window is None:
            self.extend_window = Overlay_Extend(
                minute_counts, minute_durations, face_non_durations, parent=self)
        else:
            self.extend_window.set_data(minute_counts, minute_durations, face_non_durations)
        self.extend_window.show()
        self.extend_window.raise_()
        self.extend_window.activateWindow()

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
    def show_result_window(self):
        if self.result_window is None or not self.result_window.isVisible():
            self.result_window = ResultWindow()
            self.result_window.show()
        else:
            self.result_window.activateWindow()
            self.result_window.raise_()

class Overlay_Extend(QtWidgets.QWidget):
    def __init__(self, minute_counts, minute_durations, face_non_durations, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(900, 500)
        self.setWindowOpacity(0.97)
        self.minute_counts = minute_counts
        self.minute_durations = minute_durations
        self.face_non_durations = face_non_durations
        self.init_ui()
        self.update_graph()

    def set_data(self, minute_counts, minute_durations, face_non_durations):
        self.minute_counts = minute_counts
        self.minute_durations = minute_durations
        self.face_non_durations = face_non_durations
        self.update_graph()

    def init_ui(self):
        # 상단바/버튼/라벨 등 기존 Overlay와 거의 동일하게, 위치만 좌우로 늘림
        title_bar = QtWidgets.QWidget(self)
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet("background-color: #2b2b2b; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(14, 0, 8, 0)
        title_label = QtWidgets.QLabel("BATTLE STATISTICS", self)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 15px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        q_btn = QtWidgets.QToolButton(self)
        q_btn.setText("?")
        q_btn.setToolTip("도움말을 확인할 수 있습니다.")
        q_btn.setStyleSheet("background: #fff3; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        title_layout.addWidget(q_btn)
        plus_btn = QtWidgets.QToolButton(self)
        plus_btn.setText("+")
        plus_btn.setStyleSheet("background: #a9e736; color: #494; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        plus_btn.setToolTip("새 창 추가") # 추가 동작 원하면 연결
        title_layout.addWidget(plus_btn)
        close_btn = QtWidgets.QToolButton(self)
        close_btn.setText("✕")
        close_btn.setToolTip("창을 닫고 프로그램을 종료합니다")
        close_btn.setStyleSheet("background: #ff5555; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;")
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        # 라벨
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

        # 측정시작 버튼 (스타일만)
        start_btn = QtWidgets.QPushButton("측정시작", self)
        start_btn.setFixedHeight(38)
        start_btn.setStyleSheet("""
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
        # 아이콘 코드 동일

        # ===== 그래프 =====
        self.canvas = FigureCanvas(plt.Figure(figsize=(8, 3.5)))
        self.ax = self.canvas.figure.subplots()

        # 전체 레이아웃
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(title_bar)
        main_layout.addWidget(center)
        main_layout.addWidget(self.canvas, stretch=2)
        main_layout.addWidget(start_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_layout.addSpacing(10)

    def update_graph(self):
        ax = self.ax
        ax.clear()
        minutes = len(self.minute_counts)
        x = np.arange(minutes)
        counts = np.array(self.minute_counts)
        durs = np.array(self.minute_durations)
        non_measured = np.array(self.face_non_durations)

        # 집중도 요소
        intens_counts = counts / 20
        intens_durs = durs / 2
        intensity = intens_counts + intens_durs

        # 바그래프(스택)
        p1 = ax.bar(x, intens_counts, color='#74b9ff', label='눈 감은 횟수(하늘)')
        p2 = ax.bar(x, intens_durs, bottom=intens_counts, color='#0984e3', label='눈 감은 시간(파랑)')

        # 오차 마스킹(회색, 위에서부터)
        for idx, (x0, y, ratio) in enumerate(zip(x, intensity, non_measured / 60)):
            if ratio > 0:
                # 바 위에서부터 마스킹
                bar_top = y
                bar_height = y * ratio
                ax.bar(x0, bar_height, width=0.8, color='#636e72', alpha=0.45, bottom=bar_top - bar_height, zorder=5)

        ax.set_xlabel("측정 시간(분)", fontsize=12)
        ax.set_ylabel("집중도", fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{i+1}분" for i in x], fontsize=10)
        ax.set_title("집중도 변화 (1분 단위)", fontsize=16, weight='bold')
        ax.legend(fontsize=10, loc='upper right')
        ax.set_ylim(0, max(intensity)*1.25 if len(intensity) > 0 else 1)
        ax.grid(axis='y', linestyle='--', alpha=0.2)
        self.canvas.draw()

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

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = Overlay_Style()
    win.show()
    sys.exit(app.exec())
