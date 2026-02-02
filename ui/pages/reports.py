from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from ui.styles import Theme
from datetime import datetime

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        lbl = QLabel("INCIDENT REPORTS")
        lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.COLOR_TEXT_MAIN};")
        layout.addWidget(lbl)
        
        # Reports Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "TIMESTAMP", "SEVERITY", "DESCRIPTION", "STATUS"])
        
        # Column Resizing
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # TS
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents) # Severity
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)          # Description (Fill rest)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # Status
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Enable Word Wrap
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
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
                padding: 10px;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {Theme.COLOR_BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {Theme.COLOR_BORDER};
                color: {Theme.COLOR_ACCENT};
                border-left: 2px solid {Theme.COLOR_ACCENT};
            }}
        """)
        
        layout.addWidget(self.table)
        
        # Dummy Instructions
        instr = QLabel("Select a report to view full forensic details (Not implemented in prototype)")
        instr.setStyleSheet(f"color: {Theme.COLOR_TEXT_DIM}; margin-top: 10px;")
        layout.addWidget(instr)

    def add_report(self, report_data):
        # report_data = {id, severity, description, status}
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Items
        self.table.setItem(row, 0, QTableWidgetItem(str(report_data.get("id", "N/A"))))
        self.table.setItem(row, 1, QTableWidgetItem(ts))
        
        sev_item = QTableWidgetItem(report_data.get("severity", "INFO"))
        sev_color = Theme.COLOR_CLEAN
        if report_data.get("severity") == "CRITICAL": sev_color = Theme.COLOR_MALWARE
        elif report_data.get("severity") == "HIGH": sev_color = Theme.COLOR_SUS
        sev_item.setForeground(QColor(sev_color))
        self.table.setItem(row, 2, sev_item)
        
        self.table.setItem(row, 3, QTableWidgetItem(report_data.get("description", "")))
        self.table.setItem(row, 4, QTableWidgetItem(report_data.get("status", "OPEN")))
