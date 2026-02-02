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
        
        # Main Layout (Centered Frame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Frame
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLOR_BG};
                border: 2px solid {Theme.COLOR_MALWARE};
                border-radius: 6px;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(Theme.COLOR_MALWARE))
        shadow.setOffset(0, 0)
        self.frame.setGraphicsEffect(shadow)
        
        layout.addWidget(self.frame)
        
        # Inner Layout
        inner = QVBoxLayout(self.frame)
        inner.setContentsMargins(20, 20, 20, 20)
        
        # Header
        hdr = QHBoxLayout()
        icon = QLabel("⚠")
        icon.setStyleSheet(f"font-size: 32px; color: {Theme.COLOR_MALWARE}; border: none;")
        
        title_layout = QVBoxLayout()
        title = QLabel("CRITICAL SECURITY ALERT")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.COLOR_MALWARE}; border: none;")
        subtitle = QLabel("MALICIOUS BEHAVIOR DETECTED")
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
        line.setStyleSheet(f"background-color: {Theme.COLOR_MALWARE}; max-height: 1px; border: none;")
        inner.addWidget(line)
        
        # Body
        body = QLabel(
            f"Active process <b>{pname}</b> (PID {pid}) is attempting to execute unsigned code "
            "and establish a remote connection to a known C2 server.\n\n"
            "This behavior matches the signature of <b>Trojan.Win32.Generic</b>."
            "\n\nImmediate containment is recommended."
        )
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {Theme.COLOR_TEXT_MAIN}; font-size: 13px; margin: 10px 0; border: none;")
        inner.addWidget(body)
        
        # Buttons
        btns = QHBoxLayout()
        
        btn_isolate = QPushButton("ISOLATE HOST")
        btn_isolate.setCursor(Qt.PointingHandCursor)
        btn_isolate.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.COLOR_MALWARE};
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #dc2626; }}
        """)
        btn_isolate.clicked.connect(self.accept)
        
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
