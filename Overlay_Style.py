from PyQt6 import QtWidgets, QtCore, QtGui
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Overlay_Style(QtWidgets.QWidget):
    # 측정 시작/종료 알림용 시그널
    measure_signal = QtCore.pyqtSignal(bool)  # True: 시작, False: 종료

    def __init__(self):
        super().__init__()
        self.init_ui()
        self._drag_pos = None
        self.setWindowOpacity(0.7)
        self.is_measuring = False

    def init_ui(self):
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(320, 180)

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
        help_tooltip = "이 프로그램은 눈의 감김을 감지하여 깜빡임 횟수, 감긴 시간을 측정합니다.\n+ 버튼을 눌러 측정한 결과를 바탕으로한 집중도 분석 페이지를 볼 수 있습니다"
        q_btn = QtWidgets.QToolButton(self)
        q_btn.setText("?")
        q_btn.setToolTip(help_tooltip)
        q_btn.setStyleSheet("""
            background: #fff3; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;
        """)

        self.plus_btn = QtWidgets.QToolButton(self)
        self.plus_btn.setText("+")
        self.plus_btn.setStyleSheet("""
            background: #a9e736; color: #494; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;
        """)
        self.plus_btn.clicked.connect(self.extend_window)
        
        close_btn = QtWidgets.QToolButton(self)
        close_btn.setText("✕")
        close_btn.setStyleSheet("""
            background: #ff5555; color: white; border-radius: 8px; width: 22px; height: 22px; font-weight: bold;
        """)
        close_btn.clicked.connect(QtWidgets.QApplication.quit)

        title_layout.addWidget(q_btn)
        title_layout.addWidget(self.plus_btn)
        title_layout.addWidget(close_btn)

        # 중앙 내용
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
        # 아이콘 생략(옵션)

        self.start_btn.clicked.connect(self.toggle_measure)

        # 전체 레이아웃
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(title_bar)
        main_layout.addWidget(center)
        main_layout.addStretch(1)
        main_layout.addWidget(self.start_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        main_layout.addSpacing(8)



    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        # 배경
        painter.setBrush(QtGui.QColor(42, 44, 54, 245))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)

        # 하단 빛 효과
        grad_rect = QtCore.QRectF(0, rect.height()-30, rect.width(), 30)
        grad = QtGui.QLinearGradient(0, rect.height()-30, 0, rect.height())
        grad.setColorAt(0, QtGui.QColor(200, 255, 160, 30))
        grad.setColorAt(1, QtGui.QColor(220, 240, 160, 20))
        painter.setBrush(grad)
        painter.drawRoundedRect(grad_rect, 8, 8)

    # 버튼 토글 및 시그널 송출
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

    def extend_window(self):
        if self.width() == 320 and self.height() == 180:
            self.setFixedSize(600, 400)
            self.plus_btn.setText("-")
            
        else:
            self.setFixedSize(320, 180)
            self.plus_btn.setText("+")

    # 값 업데이트 메서드
    def update_values(self, time_str, count, duration):
        self.value_labels[0].setText(time_str)
        self.value_labels[1].setText(str(count))
        self.value_labels[2].setText(f"{duration:.2f}")
        update_graph = self.update_graph


    # 마우스 드래그 등은 이전과 동일하게 필요시 추가
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
    sys.exit(app.exec())
