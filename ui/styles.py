"""Application stylesheet."""


APP_STYLE = """
QMainWindow, QWidget {
    background: #1e1e1e;
    color: #e7e7e7;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 10.5pt;
}

#topBar {
    background: #252526;
    border-bottom: 1px solid #333333;
}

#brandTitle {
    color: #f1c40f;
    font-size: 14pt;
    font-weight: 700;
}

#panelTitle {
    color: #f4f4f4;
    font-size: 16pt;
    font-weight: 700;
}

#sectionTitle {
    color: #f1c40f;
    font-size: 12pt;
    font-weight: 700;
}

#leftPanel {
    background: #242424;
    border-right: 1px solid #363636;
}

#rightPanel {
    background: #1e1e1e;
}

QPushButton {
    background: #f1c40f;
    border: 0;
    border-radius: 7px;
    color: #111111;
    font-weight: 700;
    min-height: 30px;
    padding: 6px 12px;
}

QPushButton:hover {
    background: #ffd84a;
}

QPushButton:pressed {
    background: #cfa90b;
}

QPushButton:checked {
    background: #4d4520;
    color: #f1c40f;
    border: 1px solid #f1c40f;
}

QPushButton#dangerButton {
    background: #c0392b;
    color: #ffffff;
}

QPushButton#dangerButton:hover {
    background: #e74c3c;
}

QPushButton#secondaryButton {
    background: #343434;
    color: #f1c40f;
    border: 1px solid #4b4b4b;
}

QPushButton#secondaryButton:hover {
    background: #3f3f3f;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #151515;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    color: #ffffff;
    min-height: 28px;
    padding: 4px 8px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #f1c40f;
}

QComboBox::drop-down {
    border: 0;
    width: 26px;
}

QComboBox QAbstractItemView {
    background: #202020;
    border: 1px solid #444444;
    selection-background-color: #f1c40f;
    selection-color: #111111;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QFrame#paramRow {
    background: #2b2b2b;
    border: 1px solid #383838;
    border-radius: 8px;
}

QFrame#paramRow:hover {
    border: 1px solid #565656;
}

#paramLabel {
    color: #dcdcdc;
    font-weight: 600;
}

#favoriteMark {
    color: #f1c40f;
}

#terminal {
    background: #050505;
    border: 1px solid #343434;
    border-radius: 8px;
    color: #dcdcdc;
    font-family: Consolas, "Cascadia Mono", monospace;
    font-size: 10pt;
    padding: 8px;
}

#telemetryPanel {
    background: #252525;
    border: 1px solid #383838;
    border-radius: 8px;
}

#telemetryName {
    color: #9a9a9a;
}

#telemetryGroup {
    color: #f1c40f;
    font-family: Consolas, "Cascadia Mono", monospace;
    font-weight: 700;
    padding-top: 8px;
}

#telemetryValue {
    color: #ffffff;
    font-family: Consolas, "Cascadia Mono", monospace;
    font-weight: 700;
}

#statusDot {
    background: #565656;
    border-radius: 7px;
    min-width: 14px;
    max-width: 14px;
    min-height: 14px;
    max-height: 14px;
}

#statusDot[connected="true"] {
    background: #2ecc71;
}

#statusText {
    color: #cfcfcf;
    font-weight: 600;
}

QStatusBar {
    background: #252526;
    color: #cfcfcf;
}

QScrollArea {
    background: transparent;
}

QScrollBar:vertical {
    background: #222222;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #555555;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #777777;
}

QSplitter::handle {
    background: #303030;
}
"""
