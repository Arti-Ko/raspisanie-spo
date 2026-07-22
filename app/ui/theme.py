from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

ACCENT = "#4472C4"
ACCENT_DARK = "#1F3864"
ACCENT_LIGHT = "#D9E2F3"
BACKGROUND = "#F5F6F8"
SURFACE = "#FFFFFF"
BORDER = "#C9CDD3"
TEXT = "#1A1A1A"
TEXT_MUTED = "#5B6270"

QSS = f"""
* {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QWidget {{
    background-color: {BACKGROUND};
}}

QLabel {{
    background: transparent;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background: {SURFACE};
    border-radius: 6px;
    top: -1px;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 9px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background: {SURFACE};
    color: {ACCENT_DARK};
    border: 1px solid {BORDER};
    border-bottom: 2px solid {ACCENT};
}}

QTabBar::tab:hover:!selected {{
    color: {ACCENT_DARK};
}}

QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 7px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {ACCENT_DARK};
}}

QPushButton:pressed {{
    background-color: #163055;
}}

QPushButton:disabled {{
    background-color: #B7BEC9;
    color: #EEEEEE;
}}

QLineEdit, QSpinBox, QComboBox, QDateEdit {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 8px;
    min-height: 20px;
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QTableWidget {{
    background: {SURFACE};
    alternate-background-color: {ACCENT_LIGHT};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 4px;
    selection-background-color: {ACCENT};
    selection-color: white;
}}

QTableWidget::item {{
    padding: 6px;
}}

QHeaderView::section {{
    background-color: {ACCENT};
    color: white;
    padding: 7px;
    border: none;
    font-weight: 600;
}}

QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: 600;
    color: {ACCENT_DARK};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.WindowText, QColor(TEXT))
    palette.setColor(QPalette.Base, QColor(SURFACE))
    palette.setColor(QPalette.AlternateBase, QColor(ACCENT_LIGHT))
    palette.setColor(QPalette.Text, QColor(TEXT))
    palette.setColor(QPalette.Button, QColor(ACCENT))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)

    app.setStyleSheet(QSS)
