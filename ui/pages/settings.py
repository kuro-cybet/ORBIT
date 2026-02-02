from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QSlider, QFormLayout
from PyQt5.QtCore import Qt
from ui.styles import Theme

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        lbl = QLabel("SYSTEM CONFIGURATION")
        lbl.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.COLOR_TEXT_MAIN}; margin-bottom: 20px;")
        layout.addWidget(lbl)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Items
        self.add_toggle(form_layout, "Enable Dark Mode", True)
        self.add_toggle(form_layout, "Real-time Syscall Monitoring", True)
        self.add_toggle(form_layout, "Heuristics Analysis Engine", True)
        self.add_toggle(form_layout, "Cloud Threat Intelligence", False)
        
        layout.addLayout(form_layout)
        layout.addStretch()

    def add_toggle(self, layout, text, checked):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 14px; color: {Theme.COLOR_TEXT_MAIN};")
        
        cb = QCheckBox()
        cb.setChecked(checked)
        cb.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background-color: {Theme.COLOR_BORDER};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.COLOR_ACCENT};
            }}
        """)
        
        layout.addRow(lbl, cb)
