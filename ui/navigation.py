from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from ui.styles import Theme

class Sidebar(QFrame):
    page_changed = pyqtSignal(int) # Emits index of page to switch to

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(0, 10, 20, 200); /* Semi-transparent */
                border-right: 1px solid {Theme.COLOR_BORDER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        # Branding
        lbl_brand = QLabel("ORBIT")
        lbl_brand.setAlignment(Qt.AlignCenter)
        lbl_brand.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {Theme.COLOR_ACCENT};
            letter-spacing: 3px;
            margin-bottom: 20px;
        """)
        layout.addWidget(lbl_brand)
        
        # Navigation Buttons
        self.btn_dashboard = self.create_nav_btn("DASHBOARD", 0, active=True)
        self.btn_network = self.create_nav_btn("NETWORK", 1)
        self.btn_reports = self.create_nav_btn("REPORTS", 2)
        self.btn_settings = self.create_nav_btn("SETTINGS", 3)
        
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_network)
        layout.addWidget(self.btn_reports)
        layout.addWidget(self.btn_settings)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Version
        lbl_ver = QLabel("v2.1.0")
        lbl_ver.setAlignment(Qt.AlignCenter)
        lbl_ver.setStyleSheet(f"color: {Theme.COLOR_TEXT_DIM}; font-size: 10px;")
        layout.addWidget(lbl_ver)
        
        self.buttons = [self.btn_dashboard, self.btn_network, self.btn_reports, self.btn_settings]

    def create_nav_btn(self, text, index, active=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        
        # We use a dynamic property to style checked state differently if needed, 
        # but QPushButton:checked works fine for QSS.
        btn.clicked.connect(lambda: self.on_btn_click(index))
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.COLOR_TEXT_DIM};
                border: none;
                border-radius: 4px;
                text-align: left;
                padding-left: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_MAIN};
            }}
            QPushButton:checked {{
                background-color: {Theme.COLOR_ACCENT}20; 
                color: {Theme.COLOR_ACCENT};
                border-left: 3px solid {Theme.COLOR_ACCENT};
            }}
        """)
        return btn

    def on_btn_click(self, index):
        # Update UI state
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        
        # Emit signal
        self.page_changed.emit(index)
