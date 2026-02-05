from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen
from ui.styles import Theme


class NetworkStatsCard(QWidget):
    """Animated statistics card for network metrics"""
    
    def __init__(self, title, icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self._value = 0
        self._target_value = 0
        self.trend = 0  # Positive = up, Negative = down
        self.suffix = ""
        
        self.setFixedHeight(120)
        self.setup_ui()
        
        # Animation timer for smooth value transitions
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_value)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Title with icon
        title_layout = QHBoxLayout()
        title_label = QLabel(f"{self.icon} {self.title}" if self.icon else self.title)
        title_label.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_DIM};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
            text-transform: uppercase;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Value display
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_MAIN};
            font-size: 32px;
            font-weight: bold;
            font-family: '{Theme.FONT_FAMILY_MONO}';
        """)
        layout.addWidget(self.value_label)
        
        # Trend indicator
        self.trend_label = QLabel("")
        self.trend_label.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_DIM};
            font-size: 10px;
        """)
        layout.addWidget(self.trend_label)
        layout.addStretch()
        
        # Styling
        self.setStyleSheet(f"""
            NetworkStatsCard {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 8px;
            }}
        """)
        
    def set_value(self, value, suffix="", animate=True):
        """Update the displayed value with optional animation"""
        self.suffix = suffix
        self._target_value = value
        
        if animate:
            self.anim_timer.start(30)  # Update every 30ms for smooth animation
        else:
            self._value = value
            self.update_display()
            
    def animate_value(self):
        """Smoothly animate value changes"""
        diff = self._target_value - self._value
        
        if abs(diff) < 0.1:
            self._value = self._target_value
            self.anim_timer.stop()
        else:
            self._value += diff * 0.2  # Ease towards target
            
        self.update_display()
        
    def update_display(self):
        """Update the label with current value"""
        if isinstance(self._value, float):
            display_val = f"{self._value:.1f}"
        else:
            display_val = f"{int(self._value)}"
            
        self.value_label.setText(f"{display_val}{self.suffix}")
        
    def set_trend(self, percent_change):
        """Set trend indicator (positive or negative percentage)"""
        self.trend = percent_change
        
        if percent_change > 0:
            arrow = "▲"
            color = Theme.COLOR_CLEAN
            text = f"{arrow} +{percent_change:.1f}%"
        elif percent_change < 0:
            arrow = "▼"
            color = Theme.COLOR_MALWARE
            text = f"{arrow} {percent_change:.1f}%"
        else:
            color = Theme.COLOR_TEXT_DIM
            text = "━ No change"
            
        self.trend_label.setText(text)
        self.trend_label.setStyleSheet(f"""
            color: {color};
            font-size: 10px;
            font-weight: bold;
        """)
        
    def set_critical(self, is_critical=True):
        """Add pulsing glow effect for critical metrics"""
        if is_critical:
            self.setStyleSheet(f"""
                NetworkStatsCard {{
                    background-color: {Theme.COLOR_PANEL};
                    border: 2px solid {Theme.COLOR_MALWARE};
                    border-radius: 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                NetworkStatsCard {{
                    background-color: {Theme.COLOR_PANEL};
                    border: 1px solid {Theme.COLOR_BORDER};
                    border-radius: 8px;
                }}
            """)
