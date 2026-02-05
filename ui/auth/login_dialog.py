from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from ui.styles import Theme


class LoginDialog(QDialog):
    """Login authentication dialog for ORBIT"""
    
    # Demo credentials (in production, use hashed passwords from database)
    VALID_CREDENTIALS = {
        "Kuro": "orbit2026",
        "user": "demo123"
    }
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(450, 350)
        
        # Center on screen
        self.center_on_screen()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create frame
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLOR_BG};
                border: 2px solid {Theme.COLOR_ACCENT};
                border-radius: 8px;
            }}
        """)
        
        # Add glow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(Theme.COLOR_ACCENT))
        shadow.setOffset(0, 0)
        self.frame.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.frame)
        
        # Frame layout
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        frame_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title = QLabel("ORBIT ACCESS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {Theme.COLOR_ACCENT};
            letter-spacing: 3px;
        """)
        
        subtitle = QLabel("AUTHENTICATION REQUIRED")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {Theme.COLOR_TEXT_DIM};
            letter-spacing: 2px;
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        frame_layout.addLayout(header_layout)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"""
            background-color: {Theme.COLOR_ACCENT};
            max-height: 1px;
            border: none;
        """)
        frame_layout.addWidget(divider)
        
        # Username field
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {Theme.COLOR_TEXT_MAIN}; font-weight: bold;")
        frame_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 240, 255, 10);
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                padding: 10px;
                color: {Theme.COLOR_TEXT_MAIN};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.COLOR_ACCENT};
                background-color: rgba(0, 240, 255, 20);
            }}
        """)
        frame_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {Theme.COLOR_TEXT_MAIN}; font-weight: bold;")
        frame_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 240, 255, 10);
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
                padding: 10px;
                color: {Theme.COLOR_TEXT_MAIN};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Theme.COLOR_ACCENT};
                background-color: rgba(0, 240, 255, 20);
            }}
        """)
        self.password_input.returnPressed.connect(self.attempt_login)
        frame_layout.addWidget(self.password_input)
        
        # Error message
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"""
            color: {Theme.COLOR_MALWARE};
            font-size: 12px;
            min-height: 20px;
        """)
        frame_layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel button
        btn_cancel = QPushButton("CANCEL")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Theme.COLOR_TEXT_DIM};
                color: {Theme.COLOR_TEXT_DIM};
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {Theme.COLOR_MALWARE};
                color: {Theme.COLOR_MALWARE};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        # Login button
        btn_login = QPushButton("LOGIN")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.COLOR_ACCENT};
                color: #000000;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #00d4e6;
            }}
        """)
        btn_login.clicked.connect(self.attempt_login)
        
        button_layout.addStretch()
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_login)
        frame_layout.addLayout(button_layout)
        
        # Focus on username field
        self.username_input.setFocus()
    
    def center_on_screen(self):
        """Center the dialog on the screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def attempt_login(self):
        """Validate credentials and accept/reject dialog"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Check credentials
        if username in self.VALID_CREDENTIALS:
            if self.VALID_CREDENTIALS[username] == password:
                # Success
                self.accept()
                return
        
        # Failed
        self.show_error("Invalid username or password")
        self.password_input.clear()
        self.password_input.setFocus()
    
    def show_error(self, message):
        """Display error message"""
        self.error_label.setText(f"⚠ {message}")
        
        # Shake animation effect (optional enhancement)
        # For now, just show the message
