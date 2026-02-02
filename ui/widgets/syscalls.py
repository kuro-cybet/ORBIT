import random
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QFont

from ui.styles import Theme

# ================= CUSTOM COMPONENT: SYSCALL BAR CHART =================
class SyscallChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(180)
        self.syscalls = {
            "OPEN": 10,
            "READ": 25,
            "WRITE": 8,
            "EXEC": 2,
            "CONNECT": 5
        }
        self.target_values = self.syscalls.copy()
        self.status = "Clean"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50) # Update loop

    def set_status(self, status):
        self.status = status

    def update_simulation(self):
        # 1. Update targets loosely
        for k in self.target_values:
            change = random.randint(-5, 5)
            self.target_values[k] = max(0, min(100, self.target_values[k] + change))
        
        # Malware Spikes
        if self.status == "Malware":
            self.target_values["EXEC"] = max(self.target_values["EXEC"], random.randint(60, 100))
            self.target_values["CONNECT"] = max(self.target_values["CONNECT"], random.randint(50, 90))

        # 2. Lerp current values to targets (smooth animation)
        for k in self.syscalls:
            curr = self.syscalls[k]
            target = self.target_values[k]
            self.syscalls[k] = curr + (target - curr) * 0.1
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(Theme.COLOR_PANEL))

        keys = list(self.syscalls.keys())
        bar_height = 20
        gap = 10
        start_y = 40
        max_val = 120
        
        painter.setFont(QFont(Theme.FONT_FAMILY_MONO, 9))

        for i, k in enumerate(keys):
            val = self.syscalls[k]
            y = start_y + i * (bar_height + gap)
            
            # Label
            painter.setPen(QColor(Theme.COLOR_TEXT_DIM))
            painter.drawText(10, int(y + 15), k)
            
            # Bar Background
            bar_x = 80
            bar_w = self.width() - 100
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(Theme.COLOR_BORDER))
            painter.drawRoundedRect(bar_x, int(y), int(bar_w), bar_height, 2, 2)
            
            # Bar Fill
            fill_w = (val / max_val) * bar_w
            
            color = Theme.COLOR_CLEAN
            if k in ["EXEC", "CONNECT"]:
                if val > 60: color = Theme.COLOR_MALWARE
                elif val > 40: color = Theme.COLOR_SUS
            
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(bar_x, int(y), int(fill_w), bar_height, 2, 2)
            
            # Value Text
            painter.setPen(QColor(Theme.COLOR_TEXT_DIM))
            painter.drawText(bar_x + int(fill_w) + 10, int(y + 15), str(int(val)))

        painter.setPen(QColor(Theme.COLOR_TEXT_DIM))
        painter.setFont(QFont(Theme.FONT_FAMILY_MONO, 10, QFont.Bold))
        painter.drawText(10, 20, "SYSTEM CALL ACTIVITY")


# ================= CUSTOM COMPONENT: LIVE SYSCALL LOG =================
class SyscallLogWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["TIME", "PID", "SYSCALL"])
        
        # Styling
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # Time
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # PID
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)          # Syscall
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Headers
        self.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_DIM};
                padding: 4px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        
        # Rows
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_MAIN};
                font-family: '{Theme.FONT_FAMILY_MONO}';
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 2px 4px;
                border-bottom: 1px solid {Theme.COLOR_BORDER};
            }}
        """)
        
        self.max_rows = 50
        
    def add_syscall(self, pid, name, call_type, status):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        self.insertRow(0)
        
        # Time
        t_item = QTableWidgetItem(ts)
        t_item.setForeground(QColor(Theme.COLOR_TEXT_DIM))
        self.setItem(0, 0, t_item)
        
        # PID
        p_item = QTableWidgetItem(f"{pid}")
        if status == "Malware": p_item.setForeground(QColor(Theme.COLOR_MALWARE))
        elif status == "Suspicious": p_item.setForeground(QColor(Theme.COLOR_SUS))
        else: p_item.setForeground(QColor(Theme.COLOR_CLEAN))
        self.setItem(0, 1, p_item)
        
        # Syscall
        s_item = QTableWidgetItem(f"{call_type} ({name})")
        s_item.setForeground(QColor(Theme.COLOR_TEXT_MAIN))
        self.setItem(0, 2, s_item)
        
        # Trim
        if self.rowCount() > self.max_rows:
            self.removeRow(self.max_rows)
