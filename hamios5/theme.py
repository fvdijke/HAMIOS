"""
HAMIOS v5 — Thema & kleurconstanten (PySide6)
Gebaseerd op de Midnight-stijl van v4.
"""

# Kleuren (hex strings voor Qt stylesheets)
BG_ROOT    = "#1A1C1F"
BG_PANEL   = "#22252A"
BG_SURFACE = "#2A2E35"
BG_HOVER   = "#32373F"
ACCENT     = "#C8A84B"
TEXT_H1    = "#F0E6C8"
TEXT_BODY  = "#B0B8C4"
TEXT_DIM   = "#606870"
BORDER     = "#383E47"

# Afmetingen
HDR_H      = 42     # header hoogte in pixels
PANEL_GRID = 10     # snap-raster
TITLE_H    = 26     # paneel-titelbalk hoogte

# Globaal Qt stylesheet
QSS = f"""
* {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
    color: {TEXT_BODY};
}}
QMainWindow, QWidget#desktop {{
    background-color: {BG_ROOT};
}}
QWidget#header {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}
QPushButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_H1};
    border: none;
    padding: 3px 10px;
    border-radius: 2px;
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
}}
QPushButton#accent {{
    color: {ACCENT};
}}
QPushButton#exit {{
    background-color: #5A1010;
    color: {TEXT_H1};
}}
QPushButton#exit:hover {{
    background-color: #8B1A1A;
}}
QLabel {{
    background: transparent;
}}
QLabel#title {{
    color: {ACCENT};
    font-size: 13pt;
    font-weight: bold;
}}
QLabel#time_local {{
    color: {TEXT_H1};
    font-size: 10pt;
    font-weight: bold;
}}
QLabel#time_utc {{
    color: {TEXT_DIM};
    font-size: 10pt;
}}
"""
