"""
ui.theme
========
Defines the application's dark theme using a Qt stylesheet (QSS).

The stylesheet is applied once at the QApplication level and is
automatically propagated to all widgets and dialogs.

Color palette:
    bg_color       #121212
    card_color     #1e1e1e
    accent_color   #10e09b
    text_color     #ffffff
    text_disabled  #555555
    border_color   #333333
"""

COLOR_BG = "#121212"
COLOR_CARD = "#1e1e1e"
COLOR_ACCENT = "#10e09b"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_DISABLED = "#555555"
COLOR_BORDER = "#333333"
COLOR_ACCENT_TEXT_ON = "#000000"

DARK_QSS = f"""
QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-family: "Segoe UI";
    font-size: 10pt;
}}

QMainWindow, QDialog {{
    background-color: {COLOR_BG};
}}

QGroupBox {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: {COLOR_ACCENT};
}}

QLabel {{
    background: transparent;
}}
QLabel:disabled {{
    color: {COLOR_TEXT_DISABLED};
}}

QPushButton {{
    background-color: #333333;
    color: {COLOR_TEXT};
    border: none;
    border-radius: 3px;
    padding: 6px 12px;
}}
QPushButton:hover {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_ACCENT_TEXT_ON};
}}
QPushButton:disabled {{
    background-color: #252525;
    color: {COLOR_TEXT_DISABLED};
}}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    padding: 3px;
    selection-background-color: {COLOR_ACCENT};
    selection-color: {COLOR_ACCENT_TEXT_ON};
}}
QLineEdit:disabled, QTextEdit:disabled {{
    background-color: #151515;
    color: {COLOR_TEXT_DISABLED};
}}

QComboBox {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    padding: 3px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT};
    selection-background-color: {COLOR_ACCENT};
    selection-color: {COLOR_ACCENT_TEXT_ON};
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {COLOR_BORDER};
    background: {COLOR_CARD};
}}
QCheckBox::indicator:checked {{
    background: {COLOR_ACCENT};
    border: 1px solid {COLOR_ACCENT};
}}

QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
}}
QTabBar::tab {{
    background: #2d2d2d;
    color: {COLOR_TEXT};
    padding: 6px 12px;
}}
QTabBar::tab:selected {{
    background: {COLOR_ACCENT};
    color: {COLOR_ACCENT_TEXT_ON};
}}

QTableWidget, QTreeWidget, QListWidget {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT};
    gridline-color: {COLOR_BORDER};
    border: 1px solid {COLOR_BORDER};
}}
QTableWidget::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_ACCENT_TEXT_ON};
}}
QHeaderView::section {{
    background-color: #2d2d2d;
    color: {COLOR_TEXT};
    border: none;
    padding: 4px;
}}

QMenuBar {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
}}
QMenuBar::item:selected {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_ACCENT_TEXT_ON};
}}
QMenu {{
    background-color: {COLOR_CARD};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
}}
QMenu::item:selected {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_ACCENT_TEXT_ON};
}}

QScrollBar:vertical {{
    background: {COLOR_BG};
    width: 12px;
}}
QScrollBar::handle:vertical {{
    background: #333333;
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QStatusBar {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT_DISABLED};
}}
"""
