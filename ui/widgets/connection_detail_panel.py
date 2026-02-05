from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QTabWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal
from PyQt5.QtGui import QFont
from ui.styles import Theme


class ConnectionDetailPanel(QWidget):
    """Sliding detail panel for connection information"""
    
    closed = pyqtSignal()
    action_block = pyqtSignal(dict)
    action_whitelist = pyqtSignal(dict)
    action_report = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection_data = None
        self.is_visible = False
        
        self.setFixedWidth(400)
        self.setup_ui()
        
        # Initially hidden off-screen
        self.hide()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLOR_BORDER};
                border-bottom: 2px solid {Theme.COLOR_ACCENT};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title = QLabel("CONNECTION DETAILS")
        title.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_MAIN};
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {Theme.COLOR_TEXT_DIM};
                color: {Theme.COLOR_TEXT_MAIN};
                border-radius: 15px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {Theme.COLOR_MALWARE};
                border-color: {Theme.COLOR_MALWARE};
            }}
        """)
        close_btn.clicked.connect(self.slide_out)
        header_layout.addWidget(close_btn)
        
        main_layout.addWidget(header)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Theme.COLOR_PANEL};
                border: none;
            }}
        """)
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        
        # Tabs for different info sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Theme.COLOR_BORDER};
                background-color: {Theme.COLOR_PANEL};
            }}
            QTabBar::tab {{
                background-color: {Theme.COLOR_BG};
                color: {Theme.COLOR_TEXT_DIM};
                padding: 8px 16px;
                border: 1px solid {Theme.COLOR_BORDER};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {Theme.COLOR_PANEL};
                color: {Theme.COLOR_ACCENT};
                border-bottom: 2px solid {Theme.COLOR_ACCENT};
            }}
        """)
        
        # Overview tab
        self.overview_widget = QWidget()
        self.overview_layout = QVBoxLayout(self.overview_widget)
        self.overview_layout.setSpacing(10)
        self.tabs.addTab(self.overview_widget, "Overview")
        
        # Process tab
        self.process_widget = QWidget()
        self.process_layout = QVBoxLayout(self.process_widget)
        self.process_layout.setSpacing(10)
        self.tabs.addTab(self.process_widget, "Process")
        
        # Timeline tab
        self.timeline_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_widget)
        self.timeline_layout.setSpacing(10)
        self.tabs.addTab(self.timeline_widget, "Timeline")
        
        self.content_layout.addWidget(self.tabs)
        
        # Action buttons
        actions_frame = QFrame()
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(10)
        
        self.btn_block = self.create_action_btn("🚫 BLOCK CONNECTION", Theme.COLOR_MALWARE)
        self.btn_whitelist = self.create_action_btn("✓ WHITELIST", Theme.COLOR_CLEAN)
        self.btn_report = self.create_action_btn("📋 GENERATE REPORT", Theme.COLOR_ACCENT)
        
        self.btn_block.clicked.connect(lambda: self.action_block.emit(self.connection_data))
        self.btn_whitelist.clicked.connect(lambda: self.action_whitelist.emit(self.connection_data))
        self.btn_report.clicked.connect(lambda: self.action_report.emit(self.connection_data))
        
        actions_layout.addWidget(self.btn_block)
        actions_layout.addWidget(self.btn_whitelist)
        actions_layout.addWidget(self.btn_report)
        
        self.content_layout.addWidget(actions_frame)
        self.content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Panel styling
        self.setStyleSheet(f"""
            ConnectionDetailPanel {{
                background-color: {Theme.COLOR_PANEL};
                border-left: 2px solid {Theme.COLOR_ACCENT};
            }}
        """)
        
    def create_action_btn(self, text, color):
        """Create styled action button"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 2px solid {color};
                color: {color};
                padding: 12px;
                font-weight: bold;
                border-radius: 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {color}30;
            }}
            QPushButton:pressed {{
                background-color: {color}50;
            }}
        """)
        return btn
        
    def create_info_row(self, label, value, value_color=None):
        """Create a label-value info row"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_DIM};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        layout.addWidget(lbl)
        
        val = QLabel(str(value))
        val.setWordWrap(True)
        val.setStyleSheet(f"""
            color: {value_color or Theme.COLOR_TEXT_MAIN};
            font-size: 13px;
            font-family: '{Theme.FONT_FAMILY_MONO}';
        """)
        layout.addWidget(val)
        
        return container
        
    def show_connection(self, connection_data):
        """Display connection details and slide in"""
        self.connection_data = connection_data
        self.populate_tabs()
        self.slide_in()
        
    def populate_tabs(self):
        """Populate tab content with connection data"""
        if not self.connection_data:
            return
            
        # Clear existing content
        self.clear_layout(self.overview_layout)
        self.clear_layout(self.process_layout)
        self.clear_layout(self.timeline_layout)
        
        # Overview tab
        status = self.connection_data.get('status', 'Unknown')
        status_color = Theme.COLOR_CLEAN
        if status == 'Malware':
            status_color = Theme.COLOR_MALWARE
        elif status == 'Suspicious':
            status_color = Theme.COLOR_SUS
            
        self.overview_layout.addWidget(
            self.create_info_row("STATUS", status.upper(), status_color)
        )
        self.overview_layout.addWidget(
            self.create_info_row("PROTOCOL", self.connection_data.get('proto', 'N/A'))
        )
        self.overview_layout.addWidget(
            self.create_info_row("LOCAL ADDRESS", self.connection_data.get('local', 'N/A'))
        )
        self.overview_layout.addWidget(
            self.create_info_row("REMOTE ADDRESS", self.connection_data.get('remote', 'N/A'))
        )
        self.overview_layout.addWidget(
            self.create_info_row("STATE", self.connection_data.get('state', 'N/A'))
        )
        self.overview_layout.addWidget(
            self.create_info_row("DURATION", self.connection_data.get('duration', 'N/A'))
        )
        self.overview_layout.addWidget(
            self.create_info_row("DATA TRANSFERRED", self.connection_data.get('bytes', 'N/A'))
        )
        self.overview_layout.addStretch()
        
        # Process tab
        self.process_layout.addWidget(
            self.create_info_row("PROCESS NAME", self.connection_data.get('process', 'Unknown'))
        )
        self.process_layout.addWidget(
            self.create_info_row("PID", self.connection_data.get('pid', 'N/A'))
        )
        self.process_layout.addWidget(
            self.create_info_row("RISK SCORE", f"{self.connection_data.get('risk', 0)}%")
        )
        self.process_layout.addStretch()
        
        # Timeline tab
        timeline_info = QLabel("Connection established\nData transfer in progress\nMonitoring active")
        timeline_info.setStyleSheet(f"""
            color: {Theme.COLOR_TEXT_DIM};
            font-family: '{Theme.FONT_FAMILY_MONO}';
            font-size: 12px;
        """)
        self.timeline_layout.addWidget(timeline_info)
        self.timeline_layout.addStretch()
        
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def slide_in(self):
        """Animate panel sliding in from right"""
        if self.is_visible:
            return
            
        self.show()
        self.is_visible = True
        
    def slide_out(self):
        """Animate panel sliding out to right"""
        if not self.is_visible:
            return
            
        self.hide()
        self.is_visible = False
        self.closed.emit()
