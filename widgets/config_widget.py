"""Configuration editor widget for MAVLink CLI parameters."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.config_schema import PARAMETERS, ParameterDef


class ConfigWidget(QWidget):
    """Scrollable MAVLink parameter form with change tracking."""

    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._widgets: dict[str, QWidget] = {}
        self._rows: dict[str, QWidget] = {}
        self._original: dict[str, Any] = {}
        self._favorites_only = False
        self._active_group = "TX"

        title = QLabel("MAVLink Module")
        title.setObjectName("panelTitle")

        self.group_combo = QComboBox()
        self.group_combo.addItem("Setup TX", "TX")
        self.group_combo.addItem("Setup RX", "RX")
        self.group_combo.currentIndexChanged.connect(self._change_group)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search parameter")
        self.search.textChanged.connect(self._apply_filters)

        self.favorite_button = QPushButton("Favorites")
        self.favorite_button.setCheckable(True)
        self.favorite_button.clicked.connect(self._toggle_favorites)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title, 1)
        header.addWidget(self.favorite_button)

        tools = QHBoxLayout()
        tools.setContentsMargins(0, 0, 0, 0)
        tools.addWidget(self.group_combo)
        tools.addWidget(self.search)

        self.form_container = QWidget()
        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(8)

        for param in PARAMETERS:
            row = self._build_row(param)
            self.form_layout.addWidget(row)
            self._rows[param.key] = row

        self.form_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("configScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.form_container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addLayout(header)
        layout.addLayout(tools)
        layout.addWidget(scroll, 1)

        self.load_config({param.key: param.default for param in PARAMETERS}, mark_clean=True)

    def load_config(self, config: dict[str, Any], mark_clean: bool = True) -> None:
        """Load config values into the form."""

        for param in PARAMETERS:
            value = config.get(param.key, param.default)
            self._set_widget_value(param, value)
        if mark_clean:
            self._original = self.current_values()

    def current_values(self) -> dict[str, Any]:
        """Return the current form state."""

        values: dict[str, Any] = {}
        for param in PARAMETERS:
            values[param.key] = self._get_widget_value(param)
        return values

    def get_changed_values(self) -> dict[str, Any]:
        """Return changed parameters in the currently selected TX/RX group."""

        current = self.current_values()
        return {
            key: value
            for key, value in current.items()
            if self._original.get(key) != value and self._is_active_group_key(key)
        }

    def active_group(self) -> str:
        """Return the active setup group, either ``TX`` or ``RX``."""

        return self._active_group

    def mark_clean(self) -> None:
        """Treat current values as saved/original values."""

        self._original = self.current_values()

    def _build_row(self, param: ParameterDef) -> QWidget:
        row = QFrame()
        row.setObjectName("paramRow")
        row.setProperty("favorite", param.favorite)

        label = QLabel(param.label)
        label.setObjectName("paramLabel")
        label.setToolTip(param.description)
        label.setMinimumWidth(148)

        star = QLabel("*" if param.favorite else "")
        star.setObjectName("favoriteMark")
        star.setFixedWidth(18)
        star.setAlignment(Qt.AlignmentFlag.AlignCenter)

        editor = self._create_editor(param)
        self._widgets[param.key] = editor

        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        layout.addWidget(star)
        layout.addWidget(label)
        layout.addWidget(editor, 1)
        return row

    def _create_editor(self, param: ParameterDef) -> QWidget:
        if param.field_type == "enum":
            editor = QComboBox()
            editor.addItems(param.options)
            editor.currentTextChanged.connect(lambda _value: self.changed.emit())
            return editor

        if param.field_type == "bool":
            editor = QCheckBox()
            editor.setText("Enabled")
            editor.stateChanged.connect(lambda _value: self.changed.emit())
            return editor

        if param.field_type == "int":
            editor = QSpinBox()
            editor.setRange(int(param.minimum or 0), int(param.maximum or 999999))
            editor.setSingleStep(int(param.step))
            editor.valueChanged.connect(lambda _value: self.changed.emit())
            return editor

        if param.field_type == "float":
            editor = QDoubleSpinBox()
            editor.setRange(float(param.minimum or 0), float(param.maximum or 999999))
            editor.setSingleStep(float(param.step))
            editor.setDecimals(2)
            editor.valueChanged.connect(lambda _value: self.changed.emit())
            return editor

        editor = QLineEdit()
        editor.textChanged.connect(lambda _value: self.changed.emit())
        return editor

    def _get_widget_value(self, param: ParameterDef) -> Any:
        widget = self._widgets[param.key]
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QSpinBox):
            return widget.value()
        if isinstance(widget, QDoubleSpinBox):
            return widget.value()
        if isinstance(widget, QLineEdit):
            return widget.text()
        return None

    def _set_widget_value(self, param: ParameterDef, value: Any) -> None:
        widget = self._widgets[param.key]
        widget.blockSignals(True)
        try:
            if isinstance(widget, QComboBox):
                text = str(value)
                index = widget.findText(text)
                if index < 0:
                    widget.addItem(text)
                    index = widget.findText(text)
                widget.setCurrentIndex(index)
            elif isinstance(widget, QCheckBox):
                if isinstance(value, str):
                    widget.setChecked(value.strip().lower() in {"1", "true", "yes", "on", "enabled"})
                else:
                    widget.setChecked(bool(value))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(value))
            elif isinstance(widget, QLineEdit):
                widget.setText(str(value))
        finally:
            widget.blockSignals(False)

    def _toggle_favorites(self) -> None:
        self._favorites_only = self.favorite_button.isChecked()
        self._apply_filters()

    def _change_group(self) -> None:
        self._active_group = str(self.group_combo.currentData() or "TX")
        self._apply_filters()

    def _is_active_group_key(self, key: str) -> bool:
        for param in PARAMETERS:
            if param.key == key:
                return param.group == self._active_group
        return False

    def _apply_filters(self) -> None:
        needle = self.search.text().strip().lower()
        for param in PARAMETERS:
            row = self._rows[param.key]
            matches_search = needle in param.key.lower() or needle in param.description.lower()
            matches_favorite = not self._favorites_only or param.favorite
            matches_group = param.group == self._active_group
            row.setVisible(matches_search and matches_favorite and matches_group)
