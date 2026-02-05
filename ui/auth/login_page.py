from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.styles import Theme
from security_config import SecurityConfig
from utils.validators import InputValidator


class LoginPage(QMainWindow):
    """Full-page login screen for ORBIT"""
    
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.security = SecurityConfig()
        self.setWindowTitle("ORBIT - Login")
        self.setFixedSize(1000, 600)
        
        # Center on screen
        self.center_on_screen()
        
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - Branding/Info
        left_panel = QWidget()
        left_panel.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #000814, stop:1 #001d3d);
            border-right: 2px solid {Theme.COLOR_ACCENT};
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Title
        logo = QLabel("ORBIT")
        logo.setStyleSheet(f"""
            font-size: 72px;
            font-weight: bold;
            color: {Theme.COLOR_ACCENT};
            letter-spacing: 8px;
        """)
        logo.setAlignment(Qt.AlignCenter)
        
        tagline = QLabel("OS Real-time Behavioral\nInspection Tool")
        tagline.setStyleSheet(f"""
            font-size: 16px;
            color: {Theme.COLOR_TEXT_DIM};
            letter-spacing: 2px;
        """)
        tagline.setAlignment(Qt.AlignCenter)
        
        left_layout.addStretch()
        left_layout.addWidget(logo)
        left_layout.addSpacing(20)
        left_layout.addWidget(tagline)
        left_layout.addStretch()
        
        # Right side - Login form
        right_panel = QWidget()
        right_panel.setStyleSheet(f"background-color: {Theme.COLOR_BG};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(80, 0, 80, 0)
        
        # Login form container
        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        # Form title
        form_title = QLabel("Login Form")
        form_title.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {Theme.COLOR_ACCENT};
            letter-spacing: 2px;
        """)
        form_layout.addWidget(form_title)
        
        # Decorative line
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.5 {Theme.COLOR_ACCENT}, stop:1 transparent);
            border: none;
        """)
        form_layout.addWidget(line)
        form_layout.addSpacing(20)
        
        # Username label
        username_label = QLabel("User name")
        username_label.setStyleSheet(f"color: {Theme.COLOR_TEXT_DIM}; font-size: 13px;")
        form_layout.addWidget(username_label)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("fe")
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #3a3a3a;
                border: none;
                border-radius: 8px;
                padding: 15px;
                color: {Theme.COLOR_TEXT_MAIN};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                background-color: #4a4a4a;
            }}
        """)
        form_layout.addWidget(self.username_input)
        
        # Password label
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"color: {Theme.COLOR_TEXT_DIM}; font-size: 13px;")
        form_layout.addWidget(password_label)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #3a3a3a;
                border: none;
                border-radius: 8px;
                padding: 15px;
                color: {Theme.COLOR_TEXT_MAIN};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                background-color: #4a4a4a;
            }}
        """)
        self.password_input.returnPressed.connect(self.attempt_login)
        form_layout.addWidget(self.password_input)
        
        form_layout.addSpacing(10)
        
        # Login button
        btn_login = QPushButton("Login")
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.COLOR_ACCENT};
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #00d4e6;
            }}
        """)
        btn_login.clicked.connect(self.attempt_login)
        form_layout.addWidget(btn_login)
        
        # Error message
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"""
            color: {Theme.COLOR_MALWARE};
            font-size: 12px;
            min-height: 20px;
        """)
        form_layout.addWidget(self.error_label)
        
        # Links
        links_layout = QHBoxLayout()
        
        forgot_link = QLabel("Forgot password? <a href='#' style='color: #ff1493; text-decoration: none;'>Click Here</a>")
        forgot_link.setStyleSheet(f"color: {Theme.COLOR_TEXT_DIM}; font-size: 12px;")
        forgot_link.setOpenExternalLinks(False)
        
        signup_link = QLabel("Don't have an account? <a href='#' style='color: #ff1493; text-decoration: none;'>Click Here</a>")
        signup_link.setStyleSheet(f"color: {Theme.COLOR_TEXT_DIM}; font-size: 12px;")
        signup_link.setOpenExternalLinks(False)
        
        links_layout.addWidget(forgot_link)
        links_layout.addStretch()
        form_layout.addLayout(links_layout)
        form_layout.addWidget(signup_link)
        
        right_layout.addWidget(form_container)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, stretch=1)
        main_layout.addWidget(right_panel, stretch=1)
        
        # Focus on username
        self.username_input.setFocus()
    
    def center_on_screen(self):
        """Center the window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def attempt_login(self):
        """Validate credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input format
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Validate username format
        if not InputValidator.validate_username(username):
            self.show_error("Invalid username format")
            self.username_input.clear()
            self.username_input.setFocus()
            return
        
        # Check if account is locked
        remaining = self.security.get_remaining_attempts(username)
        if remaining == 0:
            self.show_error(f"Account locked. Try again in 15 minutes.")
            return
        
        # Verify credentials
        try:
            if self.security.verify_credentials(username, password):
                # Success - create session
                self.security.create_session(username)
                self.authenticated = True
                self.close()
                return
            else:
                # Failed authentication
                remaining = self.security.get_remaining_attempts(username)
                if remaining > 0:
                    self.show_error(f"Invalid credentials. {remaining} attempts remaining.")
                else:
                    self.show_error("Account locked due to failed attempts.")
                
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            self.show_error("Authentication error. Please try again.")
            print(f"[Security] Login error: {e}")
    
    def show_error(self, message):
        """Display error message"""
        self.error_label.setText(f"⚠ {message}")
    
    def is_authenticated(self):
        """Check if user authenticated successfully"""
        return self.authenticated
