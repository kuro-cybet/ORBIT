from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from ui.styles import Theme
import random

class NetworkPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        lbl = QLabel("NETWORK TRAFFIC MONITOR")
        lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.COLOR_TEXT_MAIN};")
        layout.addWidget(lbl)
        
        # Placeholder MAP
        map_placeholder = QLabel("[ GEO-IP MAP VISUALIZATION ACTIVE ]\n\n(Tracking Global Connections...)")
        map_placeholder.setFixedSize(800, 300)
        map_placeholder.setStyleSheet(f"""
            background-color: {Theme.COLOR_PANEL}; 
            color: {Theme.COLOR_TEXT_DIM};
            border: 2px dashed {Theme.COLOR_BORDER};
            font-family: '{Theme.FONT_FAMILY_MONO}';
        """)
        map_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(map_placeholder)
        
        # Connection Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PROTOCOL", "LOCAL ADDRESS", "REMOTE ADDRESS", "STATE"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.COLOR_PANEL};
                color: {Theme.COLOR_TEXT_MAIN};
                gridline-color: {Theme.COLOR_BORDER};
                border: 1px solid {Theme.COLOR_BORDER};
                font-family: '{Theme.FONT_FAMILY_MONO}';
            }}
            QHeaderView::section {{
                background-color: {Theme.COLOR_BG};
                color: {Theme.COLOR_TEXT_DIM};
                border: none;
                padding: 8px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
        """)
        
        layout.addWidget(self.table)
        layout.addStretch()
        
        # Initial Data
        self.connections = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.simulate_traffic)
        self.timer.start(800) # Update every 800ms
        
        # Seed initial rows
        for _ in range(8):
            self.add_fake_connection()

    def simulate_traffic(self):
        # 30% chance to add new connection
        if random.random() < 0.3:
            self.add_fake_connection()
            
        # 10% chance to remove top (simulate close)
        if len(self.connections) > 15 and random.random() < 0.1:
            self.connections.pop(0)
            self.refresh_table()

    def add_fake_connection(self):
        protocols = ["TCP"] * 8 + ["UDP"] * 2
        states = ["ESTABLISHED", "TIME_WAIT", "LISTENING", "SYN_SENT"]
        
        proto = random.choice(protocols)
        local_port = random.randint(1024, 65535)
        local = f"192.168.1.105:{local_port}"
        
        # Remote IP generation (weighted for 'suspicious' ones)
        if random.random() < 0.1:
            # Suspicious
            remote_ip = f"{random.randint(100,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
            remote_port = random.choice([80, 443, 4444, 6667])
            state = "SYN_SENT (Suspicious)"
        else:
            # Normal
            remote_ip = f"{random.randint(11,99)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
            remote_port = random.choice([80, 443, 8080])
            state = random.choice(states)
            
        remote = f"{remote_ip}:{remote_port}"
        
        conn = {"proto": proto, "local": local, "remote": remote, "state": state}
        self.connections.append(conn)
        
        # Keep list size managed
        if len(self.connections) > 20: 
            self.connections.pop(0)
            
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.connections))
        # Show newest at top for log feel, or bottom? Table usually updates in place.
        # Let's reverse so newest is top
        display_list = list(reversed(self.connections))
        
        for r, conn in enumerate(display_list):
            self.table.setItem(r, 0, QTableWidgetItem(conn["proto"]))
            self.table.setItem(r, 1, QTableWidgetItem(conn["local"]))
            self.table.setItem(r, 2, QTableWidgetItem(conn["remote"]))
            
            state_item = QTableWidgetItem(conn["state"])
            if "Suspicious" in conn["state"]:
                state_item.setForeground(QColor(Theme.COLOR_MALWARE))
            elif conn["state"] == "ESTABLISHED":
                state_item.setForeground(QColor(Theme.COLOR_CLEAN))
            else:
                state_item.setForeground(QColor(Theme.COLOR_TEXT_DIM))
                
            self.table.setItem(r, 3, state_item)
