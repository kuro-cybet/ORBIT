from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QAbstractItemView, QMessageBox, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor

from ui.styles import Theme
from ui.widgets.behavior import BehaviorGraphWidget
from ui.widgets.syscalls import SyscallChartWidget, SyscallLogWidget
from ui.widgets.alert import SecurityAlert
import random
from datetime import datetime

class DashboardPage(QWidget):
    report_generated = pyqtSignal(dict) # Signals main.py to add to reports page

    def __init__(self):
        super().__init__()
        
        # --- Layouts ---
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left Panel (Table)
        left_layout = QVBoxLayout()
        
        header_lbl = QLabel("ACTIVE PROCESSES")
        header_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.COLOR_TEXT_MAIN}; letter-spacing: 1px;")
        left_layout.addWidget(header_lbl)
        
        self.create_table()
        left_layout.addWidget(self.table)
        
        # Syscall Monitor
        self.sys_log = SyscallLogWidget()
        left_layout.addWidget(self.sys_log)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_kill = self.create_btn("TERMINATE PROCESS", Theme.COLOR_MALWARE)
        self.btn_ignore = self.create_btn("WHITELIST", "#64748b")
        self.btn_report = self.create_btn("GENERATE REPORT", Theme.COLOR_ACCENT)
        
        self.btn_kill.clicked.connect(self.action_kill)
        self.btn_ignore.clicked.connect(self.action_whitelist)
        self.btn_report.clicked.connect(self.action_report)
        
        btn_layout.addWidget(self.btn_kill)
        btn_layout.addWidget(self.btn_ignore)
        btn_layout.addWidget(self.btn_report)
        left_layout.addLayout(btn_layout)
        
        main_layout.addLayout(left_layout, 60) # 60% width
        
        # Right Panel (Visuals)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)
        
        self.graph_widget = BehaviorGraphWidget()
        right_layout.addWidget(self.graph_widget)
        
        self.syscall_widget = SyscallChartWidget()
        right_layout.addWidget(self.syscall_widget)
        
        # Log Console
        log_lbl = QLabel("EVENT TIMELINE")
        log_lbl.setStyleSheet(f"font-weight: bold; color: {Theme.COLOR_TEXT_DIM}; margin-top: 10px;")
        right_layout.addWidget(log_lbl)
        
        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {Theme.COLOR_PANEL};
                color: {Theme.COLOR_TEXT_DIM};
                border: 1px solid {Theme.COLOR_BORDER};
                font-family: '{Theme.FONT_FAMILY_MONO}';
                font-size: 12px;
                padding: 10px;
            }}
        """)
        right_layout.addWidget(self.log_console)
        
        main_layout.addLayout(right_layout, 40) # 40% width

        # --- Data & Timers ---
        self.processes = [
            {"pid": 1102, "name": "explorer.exe", "risk": 5,  "status": "Clean"},
            {"pid": 4022, "name": "chrome.exe",   "risk": 12, "status": "Clean"},
            {"pid": 9182, "name": "svchost.exe",  "risk": 2,  "status": "Clean"},
            {"pid": 6601, "name": "cmd.exe",      "risk": 45, "status": "Suspicious"},
            {"pid": 1024, "name": "winlogon.exe", "risk": 0,  "status": "Clean"},
            {"pid": 8890, "name": "unknown_svc",  "risk": 95, "status": "Malware"},
            {"pid": 5512, "name": "powershell",   "risk": 60, "status": "Suspicious"},
        ]
        
        # Track reported PIDs to avoid duplicate auto-reports
        self.reported_pids = set()
        
        # Delay auto-alerts by 5 seconds
        self.system_armed = False
        QTimer.singleShot(5000, self.arm_system)
        
        self.populate_table()
        
        # Select Malware by default
        self.table.selectRow(5) 
        self.on_selection_change()

        # Risk Update Timer
        self.risk_timer = QTimer(self)
        self.risk_timer.timeout.connect(self.simulate_risk_drift)
        self.risk_timer.start(1000)
        
        # Syscall Stream Timer
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.stream_syscall)
        self.sys_timer.start(150) # Fast updates

        self.log_event("Dashboard initialized. Monitoring subsystems active.")
        self.log_event("WARNING: High-risk anomaly detected in PID 8890 (unknown_svc).")

    def arm_system(self):
        self.system_armed = True
        self.log_event("SYSTEM ARMED: Active threat interception enabled.")

    def create_btn(self, text, color_hex):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {color_hex};
                color: {color_hex};
                padding: 10px;
                font-weight: bold;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {color_hex}20; 
            }}
            QPushButton:pressed {{
                background-color: {color_hex}40;
            }}
        """)
        return btn

    def create_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PROCESS", "PID", "RISK", "STATUS"])
        
        # Styling
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Header Style
        self.table.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_DIM};
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
        """)
        
        # Table Style
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                color: {Theme.COLOR_TEXT_MAIN};
                font-family: '{Theme.FONT_FAMILY_MONO}';
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {Theme.COLOR_BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {Theme.COLOR_BORDER};
                color: {Theme.COLOR_ACCENT};
                border-left: 2px solid {Theme.COLOR_ACCENT};
            }}
        """)
        
        self.table.itemSelectionChanged.connect(self.on_selection_change)

    def populate_table(self):
        self.table.setRowCount(len(self.processes))
        for r, p in enumerate(self.processes):
            self.update_row(r)

    def update_row(self, r):
        p = self.processes[r]
        
        # Name
        self.table.setItem(r, 0, QTableWidgetItem(p["name"]))
        
        # PID
        pid_item = QTableWidgetItem(str(p["pid"]))
        pid_item.setForeground(QColor(Theme.COLOR_TEXT_DIM))
        self.table.setItem(r, 1, pid_item)
        
        # Risk
        risk_str = f"{p['risk']}%"
        risk_item = QTableWidgetItem(risk_str)
        
        if p["risk"] > 75: risk_item.setForeground(QColor(Theme.COLOR_MALWARE))
        elif p["risk"] > 40: risk_item.setForeground(QColor(Theme.COLOR_SUS))
        else: risk_item.setForeground(QColor(Theme.COLOR_CLEAN))
        self.table.setItem(r, 2, risk_item)
        
        # Status
        status_item = QTableWidgetItem(p["status"].upper())
        if p["status"] == "Malware": status_item.setForeground(QColor(Theme.COLOR_MALWARE))
        elif p["status"] == "Suspicious": status_item.setForeground(QColor(Theme.COLOR_SUS))
        else: status_item.setForeground(QColor(Theme.COLOR_CLEAN))
        
        self.table.setItem(r, 3, status_item)

    def simulate_risk_drift(self):
        for p in self.processes:
            if p["status"] == "Terminated": continue
            change = random.randint(-2, 2)
            p["risk"] = max(0, min(100, p["risk"] + change))
            
            # Auto-Report Logic
            if self.system_armed and (p["risk"] > 85 or p["status"] == "Malware") and p["pid"] not in self.reported_pids:
                 self.create_report(p, auto=True)
            
        for r, p in enumerate(self.processes):
            risk_item = self.table.item(r, 2)
            risk_item.setText(f"{p['risk']}%")
            if p["risk"] > 75: risk_item.setForeground(QColor(Theme.COLOR_MALWARE))
            elif p["risk"] > 40: risk_item.setForeground(QColor(Theme.COLOR_SUS))
            else: risk_item.setForeground(QColor(Theme.COLOR_CLEAN))

    def stream_syscall(self):
        # Pick random process
        if not self.processes: return
        p = random.choice(self.processes)
        if p["status"] == "Terminated": return
        
        # Weighted syscalls based on status
        calls = ["NtReadFile", "NtWriteFile", "RegOpenKey", "NtClose", "NtQuerySystemInfo"]
        if p["status"] == "Malware":
            calls += ["NtCreateThread", "NtOpenProcess", "Connect (Port 4444)"]
        elif p["status"] == "Suspicious":
            calls += ["PowerShell", "WmiPrum"]
            
        call = random.choice(calls)
        self.sys_log.add_syscall(p["pid"], p["name"], call, p["status"])

    def on_selection_change(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        
        r = rows[0].row()
        p = self.processes[r]
        
        self.graph_widget.set_status(p["status"])
        self.syscall_widget.set_status(p["status"])

    def action_kill(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        r = rows[0].row()
        p = self.processes[r]
        
        if p["status"] == "Terminated": return

        reply = QMessageBox.question(self, 'Confirm Termination', 
            f"Are you sure you want to terminate {p['name']} (PID: {p['pid']})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            p["status"] = "Terminated"
            p["risk"] = 0
            self.update_row(r)
            self.log_event(f"PROCESS TERMINATED: {p['name']} (PID {p['pid']})")
            self.on_selection_change() 

    def action_whitelist(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        r = rows[0].row()
        p = self.processes[r]
        
        reply = QMessageBox.question(self, 'Confirm Whitelist', 
            f"Are you sure you want to whitelist {p['name']} (PID: {p['pid']})?\nThis will suppress further alerts for this process.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            p["status"] = "Clean"
            p["risk"] = 0
            # Prevent re-reporting
            self.reported_pids.add(p["pid"])
            
            self.update_row(r)
            self.log_event(f"PROCESS WHITELISTED: {p['name']} (PID {p['pid']}) - Future alerts suppressed.")
            self.on_selection_change() 

    def action_report(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        r = rows[0].row()
        p = self.processes[r]
        
        # Trigger manual report
        self.create_report(p, auto=False)

    def generate_analysis(self, proc):
        score = random.randint(85, 99) if proc["status"] == "Malware" else random.randint(10, 40)
        
        if proc["status"] == "Malware":
            return (
                f"CRITICAL THREAT DETECTED (Impact Score: {score}/100)\n\n"
                f"Heuristic analysis indicates {proc['name']} (PID {proc['pid']}) is exhibiting behavioral anomalies consistent with advanced persistent threats (APT).\n\n"
                f"• MEMORY: Detected code injection into lsass.exe address space.\n"
                f"• NETWORK: Attempted unauthorized outbound connection to 192.168.1.X over port 4444.\n"
                f"• DISK: Modified registry keys in HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.\n\n"
                f"RECOMMENDATION: Immediate isolation and reimaging of affected host."
            )
        elif proc["status"] == "Suspicious":
            return (
                f"SUSPICIOUS ACTIVITY (Impact Score: {score}/100)\n\n"
                f"Process {proc['name']} has triggered multiple heuristic warnings.\n"
                f"• NETWORK: High frequency of DNS requests to unknown domains.\n"
                f"• CPU: Usage spikes correlate with encrypted file operations.\n\n"
                f"RECOMMENDATION: Continue monitoring. Escalate if behavior persists."
            )
        else:
            return (
                f"ROUTINE AUDIT (Impact Score: {score}/100)\n\n"
                f"Process {proc['name']} is operating within normal parameters.\n"
                f"• SIGNATURE: Verified Microsoft Windows System Component.\n"
                f"• INTEGRITY: Valid digital signature (Hash: SHA-256 matched)."
            )

    def create_report(self, p, auto=False):
        if p["pid"] in self.reported_pids and auto:
            return # Don't spam auto reports
            
        self.reported_pids.add(p["pid"])
        
        report_id = random.randint(1000,9999)
        
        if auto:
            self.log_event(f"⚠ AUTOMATED ALERT: High-risk anomaly detected in {p['name']}. Report INC-{report_id} filed.")
        else:
             self.log_event(f"REPORT GENERATED: Incident #2024-{report_id} for PID {p['pid']}")

        # ALERT POPUP if Malware (Manual OR Auto when Armed)
        if p["status"] == "Malware":
            # If auto, only show if we are armed (redundant check but safe)
            if not auto or self.system_armed:
                alert = SecurityAlert(self, data=p)
                if alert.exec_(): 
                    # Isolate clicked
                    self.action_kill() 
                    pass
        
        # Emit data
        report_data = {
            "id": f"INC-{report_id}",
            "severity": "CRITICAL" if p["status"] == "Malware" else ("HIGH" if p["status"] == "Suspicious" else "INFO"),
            "description": self.generate_analysis(p),
            "status": "OPEN"
        }
        self.report_generated.emit(report_data)
        
        # Toast (Manual Only)
        if not auto and p["status"] != "Malware":
            QMessageBox.information(self, "Report Created", f"Incident report INC-{report_id} has been filed to the Reports tab.")

    def log_event(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_console.appendPlainText(f"[{ts}] {msg}")
