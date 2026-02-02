import random
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QFont

from ui.styles import Theme

class BehaviorGraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(220)
        self.phase = 0.0
        self.status = "Clean"
        self.points = []
        
        # Timer for 60fps animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~60fps

    def set_status(self, status):
        self.status = status

    def update_animation(self):
        self.phase += 0.1
        self.update() # Trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background: Using Panel Color
        painter.fillRect(self.rect(), QColor(Theme.COLOR_PANEL))
        
        # Grid lines
        width = self.width()
        height = self.height()
        mid_y = height / 2
        
        painter.setPen(QPen(QColor(Theme.COLOR_BORDER), 1))
        painter.drawLine(0, int(mid_y), width, int(mid_y)) # Center line
        
        # Configure wave based on status
        amplitude = 20
        freq = 0.05
        noise_level = 0
        primary_color = Theme.COLOR_CLEAN

        if self.status == "Suspicious":
            amplitude = 40
            noise_level = 5
            primary_color = Theme.COLOR_SUS
        elif self.status == "Malware":
            amplitude = 70
            freq = 0.1
            noise_level = 15
            primary_color = Theme.COLOR_MALWARE

        # Draw Wave
        path = []
        for x in range(0, width, 2):
            sine = math.sin(x * freq - self.phase)
            noise = (random.random() - 0.5) * noise_level
            y = mid_y + (sine * amplitude) + noise
            path.append((x, y))

        # Glow effect
        glow_color = QColor(primary_color)
        glow_color.setAlpha(40)
        painter.setPen(QPen(glow_color, 6))
        for i in range(len(path) - 1):
            painter.drawLine(int(path[i][0]), int(path[i][1]), int(path[i+1][0]), int(path[i+1][1]))

        # Main line
        painter.setPen(QPen(QColor(primary_color), 2))
        for i in range(len(path) - 1):
            painter.drawLine(int(path[i][0]), int(path[i][1]), int(path[i+1][0]), int(path[i+1][1]))
            
        # Overlay Text
        painter.setPen(QColor(Theme.COLOR_TEXT_DIM))
        painter.setFont(QFont(Theme.FONT_FAMILY_MONO, 10))
        painter.drawText(10, 20, "REAL-TIME BEHAVIOR ANALYSIS")
        
        painter.setPen(QColor(primary_color))
        painter.setFont(QFont(Theme.FONT_FAMILY_UI, 12, QFont.Bold))
        painter.drawText(10, 45, f"STATUS: {self.status.upper()}")
