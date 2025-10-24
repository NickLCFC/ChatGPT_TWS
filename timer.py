import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QSpinBox,
    QColorDialog, QSlider, QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont


class CountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("\u5012\u6578\u8a08\u6642\u5668")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(400, 200)

        self.label = QLabel("00:00", self)
        self.label.setFont(QFont("Arial Rounded MT Bold", 120, QFont.Bold))
        self.label.setStyleSheet("color: yellow; background-color: rgba(0,0,0,0);")
        self.label.setAlignment(Qt.AlignCenter)

        self.rmb_label = QLabel("\u7d05\u5305:\uffe50", self)
        self.rmb_label.setFont(QFont("Arial Rounded MT Bold", 36, QFont.Bold))
        self.rmb_label.setStyleSheet("color: red; background-color: rgba(0,0,0,0);")
        self.rmb_label.setAlignment(Qt.AlignCenter)
        self.rmb_label.hide()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.label)
        layout.addWidget(self.rmb_label)
        self.setLayout(layout)

        self.flash_state = True
        self.flashing = False
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.toggle_flash)

        self.rmb_amount = 0
        self.rmb_timer = QTimer(self)
        self.rmb_timer.timeout.connect(self.increase_rmb)

    def update_time(self, minutes, seconds):
        self.label.setText(f"{minutes:02d}:{seconds:02d}")

    def toggle_flash(self):
        if not self.flashing:
            return
        self.flash_state = not self.flash_state
        color = "red" if self.flash_state else "black"
        self.label.setStyleSheet(f"color: {color}; background-color: rgba(0,0,0,0);")

    def start_flashing(self):
        self.flashing = True
        self.flash_state = True
        self.flash_timer.start(1000)  # flash every second
        self.rmb_label.show()
        self.rmb_timer.start(6000)  # \u6bcf 6 \u79d2 +\uffe510

    def stop_flashing(self):
        self.flashing = False
        self.flash_timer.stop()
        self.rmb_timer.stop()
        # reset color when flashing stops
        self.label.setStyleSheet("color: yellow; background-color: rgba(0,0,0,0);")

    def reset_rmb(self):
        self.rmb_amount = 0
        self.rmb_label.setText("\u7d05\u5305:\uffe50")
        self.rmb_label.hide()

    def increase_rmb(self):
        self.rmb_amount += 10
        self.rmb_label.setText(f"\u7d05\u5305:\uffe5{self.rmb_amount}")


class Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timer Controller - \u900f\u660e\u5410\u53f8\u7248")
        self.setFixedSize(520, 260)

        # setup time spin boxes
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 99)
        self.minutes_spin.setValue(5)

        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setValue(0)

        self.color_btn = QPushButton("Choose Text Color")
        self.color_btn.clicked.connect(self.choose_color)

        # control buttons
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")
        self.reset_btn = QPushButton("Reset")
        self.minus_btn = QPushButton("-")
        self.plus_btn = QPushButton("+")
        self.help_btn = QPushButton("?")

        for btn in [self.start_btn, self.pause_btn, self.resume_btn,
                    self.reset_btn, self.minus_btn, self.plus_btn,
                    self.color_btn, self.help_btn]:
            btn.setFixedHeight(36)

        # opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.change_opacity)

        # layout
        layout = QGridLayout()
        layout.addWidget(self.minutes_spin, 0, 0)
        layout.addWidget(QLabel("Mins:"), 0, 1)
        layout.addWidget(self.seconds_spin, 0, 2)
        layout.addWidget(QLabel("Secs:"), 0, 3)
        layout.addWidget(self.color_btn, 0, 4)
        layout.addWidget(self.help_btn, 0, 5)

        layout.addWidget(self.start_btn, 1, 0, 1, 2)
        layout.addWidget(self.pause_btn, 1, 2, 1, 2)
        layout.addWidget(self.resume_btn, 1, 4, 1, 1)
        layout.addWidget(self.reset_btn, 1, 5, 1, 1)

        layout.addWidget(self.minus_btn, 2, 0, 1, 3)
        layout.addWidget(self.plus_btn, 2, 3, 1, 3)

        layout.addWidget(QLabel("Opacity:"), 3, 0)
        layout.addWidget(self.opacity_slider, 3, 1, 1, 5)

        self.setLayout(layout)

        # logic
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.display = CountdownWindow()
        self.display.show()

        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.timer.stop)
        self.resume_btn.clicked.connect(lambda: self.timer.start(1000))
        self.reset_btn.clicked.connect(self.reset_timer)
        self.minus_btn.clicked.connect(lambda: self.adjust_time(-1))
        self.plus_btn.clicked.connect(lambda: self.adjust_time(1))

        self.total_seconds = 0

    def start_timer(self):
        mins = self.minutes_spin.value()
        secs = self.seconds_spin.value()
        self.total_seconds = mins * 60 + secs
        self.display.update_time(mins, secs)  # show starting time
        self.display.stop_flashing()
        self.display.reset_rmb()
        self.timer.start(1000)

    def update_time(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1
            mins, secs = divmod(self.total_seconds, 60)
            self.display.update_time(mins, secs)
            self.minutes_spin.setValue(mins)
            self.seconds_spin.setValue(secs)
        else:
            self.timer.stop()
            self.display.start_flashing()

    def reset_timer(self):
        self.timer.stop()
        self.total_seconds = 0
        self.display.update_time(0, 0)
        self.display.stop_flashing()
        self.display.reset_rmb()
        self.minutes_spin.setValue(0)
        self.seconds_spin.setValue(0)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.display.label.setStyleSheet(
                f"color: {color.name()}; background-color: rgba(0,0,0,0);"
            )

    def adjust_time(self, delta):
        # adjust by the number of minutes currently set in the minutes spin box
        step_minutes = self.minutes_spin.value()
        self.total_seconds = max(0, self.total_seconds + delta * step_minutes * 60)
        mins, secs = divmod(self.total_seconds, 60)
        self.minutes_spin.setValue(mins)
        self.seconds_spin.setValue(secs)
        self.display.update_time(mins, secs)

    def change_opacity(self, value):
        self.display.setWindowOpacity(value / 100)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show()
    sys.exit(app.exec_())
