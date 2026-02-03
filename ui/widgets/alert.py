from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from ui.styles import Theme

class SecurityAlert(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 280)
        
        self.data = data or {}
        pname = self.data.get("name", "Unknown")
        pid = self.data.get("pid", "0000")
        status = self.data.get("status", "Malware")
        
        # Determine colors and text based on threat level
        if status == "Suspicious":
            alert_color = "#f59e0b"  # Amber/Yellow
            icon_text = "⚠"
            title_text = "SUSPICIOUS ACTIVITY DETECTED"
            subtitle_text = "POTENTIAL THREAT IDENTIFIED"
            body_text = (
                f"Active process <b>{pname}</b> (PID {pid}) is exhibiting suspicious behavior patterns "
                "including unusual system calls and network activity.\\n\\n"
                "This activity may indicate reconnaissance or lateral movement attempts."
                "\\n\\nReview and investigation recommended."
            )
            btn_text = "INVESTIGATE"
        else:  # Malware
            alert_color = Theme.COLOR_MALWARE  # Red
            icon_text = "⚠"
            title_text = "CRITICAL SECURITY ALERT"
            subtitle_text = "MALICIOUS BEHAVIOR DETECTED"
            body_text = (
                f"Active process <b>{pname}</b> (PID {pid}) is attempting to execute unsigned code "
                "and establish a remote connection to a known C2 server.\\n\\n"
                "This behavior matches the signature of <b>Trojan.Win32.Generic</b>."
                "\\n\\nImmediate containment is recommended."
            )
            btn_text = "ISOLATE HOST"
        
        # Main Layout (Centered Frame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Frame
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLOR_BG};
                border: 2px solid {alert_color};
                border-radius: 6px;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(alert_color))
        shadow.setOffset(0, 0)
        self.frame.setGraphicsEffect(shadow)
        
        layout.addWidget(self.frame)
        
        # Inner Layout
        inner = QVBoxLayout(self.frame)
        inner.setContentsMargins(20, 20, 20, 20)
        
        # Header
        hdr = QHBoxLayout()
        icon = QLabel(icon_text)
        icon.setStyleSheet(f"font-size: 32px; color: {alert_color}; border: none;")
        
        title_layout = QVBoxLayout()
        title = QLabel(title_text)
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {alert_color}; border: none;")
        subtitle = QLabel(subtitle_text)
        subtitle.setStyleSheet(f"font-size: 12px; color: {Theme.COLOR_TEXT_MAIN}; letter-spacing: 2px; border: none;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        hdr.addWidget(icon)
        hdr.addSpacing(15)
        hdr.addLayout(title_layout)
        hdr.addStretch()
        inner.addLayout(hdr)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {alert_color}; max-height: 1px; border: none;")
        inner.addWidget(line)
        
        # Body
        body = QLabel(body_text)
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {Theme.COLOR_TEXT_MAIN}; font-size: 13px; margin: 10px 0; border: none;")
        inner.addWidget(body)
        
        # Buttons
        btns = QHBoxLayout()
        
        btn_isolate = QPushButton(btn_text)
        btn_isolate.setCursor(Qt.PointingHandCursor)
        btn_isolate.setStyleSheet(f"""
            QPushButton {{
                background-color: {alert_color};
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {alert_color}dd; }}
        """)
        # Different actions based on threat level
        if status == "Suspicious":
            btn_isolate.clicked.connect(lambda: self.done(2))  # 2 = Navigate to reports
        else:
            btn_isolate.clicked.connect(lambda: self.done(1))  # 1 = Isolate/terminate
        
        btn_ignore = QPushButton("IGNORE ALERT")
        btn_ignore.setCursor(Qt.PointingHandCursor)
        btn_ignore.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.COLOR_TEXT_DIM};
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ color: {Theme.COLOR_TEXT_MAIN}; border-color: {Theme.COLOR_TEXT_MAIN}; }}
        """)
        btn_ignore.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(btn_ignore)
        btns.addWidget(btn_isolate)
        inner.addLayout(btns)
        
        # Pulse Animation logic (simple border flash) can go here


