from PyQt5.QtGui import QColor
import os

class Theme:
    # --- HOLO-CYAN PALETTE ---
    # Derived from the "Global Defense Grid" image
    
    # Backgrounds
    COLOR_BG = "#000000"        # Fallback black
    
    # Panels (Glassmorphism)
    # Hex with Alpha: #AARRGGBB (180 approx B4)
    COLOR_PANEL = "#B4040C18"    # Semi-transparent Dark Blue
    
    # Border (Cyan with low alpha 50 approx 32)
    COLOR_BORDER = "#3200F0FF"
    
    # Text
    COLOR_TEXT_MAIN = "#E0F7FA" # Icy White
    COLOR_TEXT_DIM = "#537c80"  # Muted Cyan radius
    
    # Accents / Status
    COLOR_ACCENT = "#00f0ff"    # Electric Cyan
    
    COLOR_CLEAN = "#00f0ff"     # Cyan (Safe)
    COLOR_SUS = "#f59e0b"       # Amber (Risk)
    COLOR_MALWARE = "#ff003c"   # Aggressive Crimson (Threat)
    
    # Fonts
    FONT_FAMILY_UI = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"

    @staticmethod
    def get_qss():
        # Get absolute path for image to avoid QSS resource issues
        bg_path = os.path.abspath("assets/bg.png").replace("\\", "/")
        
        return f"""
            QMainWindow {{ 
                background-image: url({bg_path});
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed; 
                /* scaling hack handled by QWidget if needed, but 'background-image' tiles by default. 
                   Better to use border-image on a central frame or just background-color if image fails. 
                   Let's try standard background-image scaling via QSS isn't great in Qt5.
                   The user provided a large image, so centering is safe. */
                background-color: #020617;
            }}
            
            QWidget {{
                font-family: '{Theme.FONT_FAMILY_UI}', 'sans-serif';
                font-size: 14px;
                color: {Theme.COLOR_TEXT_DIM};
            }}
            
            /* --- Scrollbars (Holo Style) --- */
            QScrollBar:vertical {{
                border: none;
                background: rgba(0,0,0,50);
                width: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.COLOR_ACCENT};
                min-height: 20px;
                border-radius: 3px;
                opacity: 0.5;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            
            /* --- Transparent Panels --- */
            QTableWidget, QPlainTextEdit, QFrame {{
                background-color: {Theme.COLOR_PANEL}; 
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
            }}
            
            /* --- Header Styling (Glass) --- */
            QHeaderView::section {{
                background-color: rgba(0, 240, 255, 20); /* Low Opacity Cyan */
                color: {Theme.COLOR_ACCENT};
                border: none;
                border-bottom: 2px solid {Theme.COLOR_ACCENT};
                padding: 4px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            /* --- Table Items --- */
            QTableWidget::item {{
                border-bottom: 1px solid rgba(0, 240, 255, 20);
                color: {Theme.COLOR_TEXT_MAIN};
            }}
            QTableWidget::item:selected {{
                background-color: rgba(0, 240, 255, 40);
                border-left: 3px solid {Theme.COLOR_ACCENT};
                color: #ffffff;
            }}
            
            /* --- Buttons (Holo) --- */
            QPushButton {{
                background-color: rgba(0,0,0,0);
                border: 1px solid {Theme.COLOR_TEXT_DIM};
                color: {Theme.COLOR_TEXT_MAIN};
                padding: 5px;
            }}
            QPushButton:hover {{
                border: 1px solid {Theme.COLOR_ACCENT};
                background-color: rgba(0, 240, 255, 20);
                color: {Theme.COLOR_ACCENT};
            }}
            
            /* --- Tooltips --- */
            QToolTip {{
                background-color: #000000;
                color: {Theme.COLOR_ACCENT};
                border: 1px solid {Theme.COLOR_ACCENT};
            }}
        """
