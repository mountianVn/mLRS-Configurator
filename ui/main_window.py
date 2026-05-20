"""Main application window."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QComboBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from core.cli_parser import MavlinkCliParser
from core.config_store import ConfigStore
from core.telemetry_parser import MavlinkTelemetryParser
from widgets.config_widget import ConfigWidget
from widgets.log_viewer import LogViewer
from widgets.telemetry_widget import TelemetryWidget


SERIAL_MANAGER_PATH = Path(__file__).resolve().parents[1] / "serial" / "serial_manager.py"
_serial_spec = importlib.util.spec_from_file_location("mavlink_serial_manager", SERIAL_MANAGER_PATH)
if _serial_spec is None or _serial_spec.loader is None:
    raise ImportError(f"Cannot load serial manager from {SERIAL_MANAGER_PATH}")
_serial_module = importlib.util.module_from_spec(_serial_spec)
sys.modules[_serial_spec.name] = _serial_module
_serial_spec.loader.exec_module(_serial_module)
SerialManager = _serial_module.SerialManager


class MainWindow(QMainWindow):
    """ELRS Configurator inspired desktop UI for MAVLink CLI modules."""

    BAUDRATES = ("57600", "115200", "230400", "460800", "921600")

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MAVLink CLI Configurator")
        self.resize(1280, 820)

        self.store = ConfigStore()
        self.parser = MavlinkCliParser()
        self.telemetry_parser = MavlinkTelemetryParser()
        self.serial = SerialManager()
        self._pending_dump: list[str] = []
        self._dump_active = False
        self._firmware_version = "Unknown"
        self._save_queue: list[str] = []
        self._saving = False

        self.config_widget = ConfigWidget()
        self.log_viewer = LogViewer()
        self.telemetry_widget = TelemetryWidget()

        self._build_ui()
        self._connect_signals()
        self._load_persisted_state()
        self.refresh_ports()

        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._animate_connection_dot)
        self._blink_timer.start(700)
        self._blink_on = True

        self._dump_timer = QTimer(self)
        self._dump_timer.setSingleShot(True)
        self._dump_timer.timeout.connect(self._finish_dump)

        self._save_timer = QTimer(self)
        self._save_timer.setInterval(50)
        self._save_timer.timeout.connect(self._send_next_save_command)

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_top_bar())
        root.addWidget(self._build_content(), 1)
        self.setCentralWidget(central)

        status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.firmware_label = QLabel("Firmware: Unknown")
        status_bar.addWidget(self.status_label, 1)
        status_bar.addPermanentWidget(self.firmware_label)
        self.setStatusBar(status_bar)

    def _build_top_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        brand = QLabel("MAVLink CLI Configurator")
        brand.setObjectName("brandTitle")
        brand.setMinimumWidth(230)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(self.BAUDRATES)
        self.baud_combo.setCurrentText("115200")

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(160)

        self.refresh_button = self._icon_button("Refresh", QStyle.StandardPixmap.SP_BrowserReload)
        self.connect_button = self._icon_button("Connect", QStyle.StandardPixmap.SP_DialogApplyButton)
        self.clear_button = self._icon_button("Clear Log", QStyle.StandardPixmap.SP_DialogResetButton)
        self.view_button = self._icon_button("View", QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.version_button = self._icon_button("Version", QStyle.StandardPixmap.SP_MessageBoxInformation)
        for button in (self.refresh_button, self.clear_button, self.view_button):
            button.setObjectName("secondaryButton")
        self.version_button.setObjectName("secondaryButton")

        self.status_dot = QLabel()
        self.status_dot.setObjectName("statusDot")
        self.status_dot.setProperty("connected", False)
        self.status_text = QLabel("Disconnected")
        self.status_text.setObjectName("statusText")

        layout.addWidget(brand)
        layout.addWidget(QLabel("Baudrate"))
        layout.addWidget(self.baud_combo)
        layout.addWidget(QLabel("COM Port"))
        layout.addWidget(self.port_combo)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.view_button)
        layout.addWidget(self.version_button)
        layout.addStretch(1)
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)
        return bar

    def _build_content(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(390)
        left_panel.setMaximumWidth(480)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.config_widget, 1)
        left_layout.addWidget(self._build_config_actions())

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(12)
        right_layout.addWidget(self.telemetry_widget)
        right_layout.addWidget(self.log_viewer, 1)
        right_layout.addWidget(self._build_console())

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([430, 850])
        return splitter

    def _build_config_actions(self) -> QWidget:
        actions = QWidget()
        layout = QVBoxLayout(actions)
        layout.setContentsMargins(14, 0, 14, 14)
        layout.setSpacing(8)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()

        self.read_button = self._icon_button("Read", QStyle.StandardPixmap.SP_ArrowDown)
        self.save_button = self._icon_button("Save", QStyle.StandardPixmap.SP_DialogSaveButton)
        self.reboot_button = self._icon_button("Reboot", QStyle.StandardPixmap.SP_BrowserReload)
        self.reboot_button.setObjectName("dangerButton")
        self.import_button = self._icon_button("Import", QStyle.StandardPixmap.SP_DialogOpenButton)
        self.export_button = self._icon_button("Export", QStyle.StandardPixmap.SP_DialogSaveButton)
        for button in (self.import_button, self.export_button):
            button.setObjectName("secondaryButton")

        row1.addWidget(self.read_button)
        row1.addWidget(self.save_button)
        row1.addWidget(self.reboot_button)
        row2.addWidget(self.import_button)
        row2.addWidget(self.export_button)
        layout.addLayout(row1)
        layout.addLayout(row2)
        return actions

    def _build_console(self) -> QWidget:
        console = QWidget()
        layout = QHBoxLayout(console)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        prompt = QLabel("CLI")
        prompt.setObjectName("sectionTitle")
        self.cli_input = QLineEdit()
        self.cli_input.setPlaceholderText("Type command and press Enter")
        self.cli_input.setFont(QFont("Consolas", 10))
        self.send_button = self._icon_button("Send", QStyle.StandardPixmap.SP_ArrowForward)
        self.send_button.setObjectName("secondaryButton")

        layout.addWidget(prompt)
        layout.addWidget(self.cli_input, 1)
        layout.addWidget(self.send_button)
        return console

    def _icon_button(self, text: str, icon: QStyle.StandardPixmap) -> QPushButton:
        button = QPushButton(text)
        button.setIcon(self.style().standardIcon(icon))
        return button

    def _connect_signals(self) -> None:
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.toggle_connection)
        self.clear_button.clicked.connect(self.log_viewer.clear)
        self.view_button.clicked.connect(self._toggle_telemetry)
        self.version_button.clicked.connect(self.request_version)
        self.read_button.clicked.connect(self.read_config)
        self.save_button.clicked.connect(self.save_config)
        self.reboot_button.clicked.connect(self.reboot_module)
        self.import_button.clicked.connect(self.import_config)
        self.export_button.clicked.connect(self.export_config)
        self.cli_input.returnPressed.connect(self.send_cli_command)
        self.send_button.clicked.connect(self.send_cli_command)

        self.serial.line_received.connect(self._handle_rx_line)
        self.serial.telemetry_received.connect(self.telemetry_widget.update_data)
        self.serial.error.connect(self._handle_error)
        self.serial.info.connect(self._handle_info)
        self.serial.connected_changed.connect(self._handle_connected_changed)

    def _load_persisted_state(self) -> None:
        settings = self.store.load_settings()
        if settings.get("baudrate"):
            self.baud_combo.setCurrentText(str(settings["baudrate"]))
        config = self.store.load_config()
        if config:
            self.config_widget.load_config(config, mark_clean=True)
            self.log_viewer.append("INFO", "Loaded last local configuration snapshot.")

    @Slot()
    def refresh_ports(self) -> None:
        current = self.port_combo.currentText()
        ports = self.serial.scan_ports()
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current and current in ports:
            self.port_combo.setCurrentText(current)
        self.log_viewer.append("INFO", f"Ports refreshed: {', '.join(ports)}")

    @Slot()
    def toggle_connection(self) -> None:
        if self.serial.is_connected:
            self.serial.disconnect()
            return

        port = self.port_combo.currentText() or "MOCK"
        baudrate = int(self.baud_combo.currentText())
        self.store.save_settings({"baudrate": baudrate, "last_port": port})
        self.serial.connect(port, baudrate)

    @Slot()
    def read_config(self) -> None:
        self._pending_dump.clear()
        self._dump_active = True
        self._send_command(self.parser.READ_COMMAND)

    @Slot()
    def save_config(self) -> None:
        if self._saving:
            self.log_viewer.append("INFO", "Save is already in progress.")
            return

        changes = self.config_widget.get_changed_values()
        if not changes:
            self.log_viewer.append("INFO", f"No changed {self.config_widget.active_group()} parameters to save.")
            return

        self._save_queue = [self.parser.build_set_command(key, value) for key, value in changes.items()]
        self._save_queue.append(self.parser.SAVE_COMMAND)
        self._saving = True
        self.save_button.setEnabled(False)
        self.status_label.setText(
            f"Saving {self.config_widget.active_group()} setup with {len(self._save_queue)} command(s)..."
        )
        self._send_next_save_command()

    @Slot()
    def _send_next_save_command(self) -> None:
        if not self._save_queue:
            self._save_timer.stop()
            self._saving = False
            self.save_button.setEnabled(True)
            self.config_widget.mark_clean()
            self.store.save_config(self.config_widget.current_values())
            self.status_label.setText("Save complete.")
            self.log_viewer.append("INFO", "Save complete. Final command was pstore;")
            return

        command = self._save_queue.pop(0)
        self._send_command(command)
        self._save_timer.start()

    @Slot()
    def reboot_module(self) -> None:
        answer = QMessageBox.question(
            self,
            "Reboot module",
            "Reboot the connected MAVLink module?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._send_command(self.parser.REBOOT_COMMAND)

    @Slot()
    def request_version(self) -> None:
        self._send_command(self.parser.VERSION_COMMAND)

    @Slot()
    def send_cli_command(self) -> None:
        command = self.cli_input.text().strip()
        if not command:
            return
        self.cli_input.clear()
        self._send_command(command)

    @Slot()
    def import_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import config", "", "JSON files (*.json)")
        if not path:
            return
        try:
            config = ConfigStore.import_config(path)
            self.config_widget.load_config(config, mark_clean=False)
            self.log_viewer.append("INFO", f"Imported config from {path}")
        except Exception as exc:
            self._handle_error(f"Import failed: {exc}")

    @Slot()
    def export_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export config", "mavlink_config.json", "JSON files (*.json)")
        if not path:
            return
        try:
            ConfigStore.export_config(path, self.config_widget.current_values())
            self.log_viewer.append("INFO", f"Exported config to {path}")
        except Exception as exc:
            self._handle_error(f"Export failed: {exc}")

    def _send_command(self, command: str) -> None:
        self.log_viewer.append("TX", command)
        self.serial.send(command)

    @Slot(str)
    def _handle_rx_line(self, line: str) -> None:
        self.log_viewer.append("RX", line)

        telemetry = self.telemetry_parser.parse_line(line)
        if telemetry:
            self.telemetry_widget.update_data(telemetry)
            return

        if line.startswith("# BEGIN CONFIG"):
            self._dump_active = True
            self._pending_dump.clear()
            self._dump_timer.stop()
            return
        if line.startswith("# END CONFIG"):
            self._dump_timer.stop()
            self._finish_dump()
            return
        if self._dump_active:
            self._pending_dump.append(line)
            self._dump_timer.start(800)

        parsed = self.parser.parse_line(line)
        if parsed is None:
            if "FW" in line.upper() or "VERSION" in line.upper():
                self._firmware_version = line
                self.firmware_label.setText(f"Firmware: {line}")
            return

        key, value = parsed
        if key in {"FW_VERSION", "VERSION"}:
            self._firmware_version = value
            self.firmware_label.setText(f"Firmware: {value}")
        elif key in {"RSSI", "LQ", "LINK_QUALITY", "VOLTAGE", "CURRENT"}:
            self._update_telemetry_from_cli(key, value)
        else:
            config = self.parser.parse_dump(line)
            if not config:
                return
            self.config_widget.load_config({**self.config_widget.current_values(), **config}, mark_clean=False)

    def _finish_dump(self) -> None:
        config = self.parser.parse_dump("\n".join(self._pending_dump))
        if config:
            merged_config = {**self.config_widget.current_values(), **config}
            self.config_widget.load_config(merged_config, mark_clean=True)
            self.store.save_config(self.config_widget.current_values())
            self.status_label.setText(f"Read {len(config)} parameters.")
            self.log_viewer.append("INFO", f"Loaded {len(config)} parameters from module.")
        self._pending_dump.clear()
        self._dump_active = False

    def _update_telemetry_from_cli(self, key: str, value: str) -> None:
        mapping = {
            "RSSI": "RSSI",
            "LQ": "Link Quality",
            "LINK_QUALITY": "Link Quality",
            "VOLTAGE": "Voltage",
            "CURRENT": "Current",
        }
        target = mapping.get(key)
        if target is not None:
            self.telemetry_widget.update_data({target: value})

    @Slot(str)
    def _handle_error(self, message: str) -> None:
        self.log_viewer.append("ERROR", message)
        self.status_label.setText(message)

    @Slot(str)
    def _handle_info(self, message: str) -> None:
        self.log_viewer.append("INFO", message)
        self.status_label.setText(message)

    @Slot(bool)
    def _handle_connected_changed(self, connected: bool) -> None:
        self.status_text.setText("Connected" if connected else "Disconnected")
        self.connect_button.setText("Disconnect" if connected else "Connect")
        icon = QStyle.StandardPixmap.SP_DialogCancelButton if connected else QStyle.StandardPixmap.SP_DialogApplyButton
        self.connect_button.setIcon(self.style().standardIcon(icon))
        self.status_dot.setProperty("connected", connected)
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        self.status_label.setText("Connected" if connected else "Disconnected")

    def _animate_connection_dot(self) -> None:
        if not self.serial.is_connected:
            self.status_dot.setStyleSheet("")
            return
        self._blink_on = not self._blink_on
        opacity_color = "#2ecc71" if self._blink_on else "#1f7a45"
        self.status_dot.setStyleSheet(f"background: {opacity_color}; border-radius: 7px;")

    def _toggle_telemetry(self) -> None:
        self.read_config()

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API
        self._save_timer.stop()
        self.store.save_config(self.config_widget.current_values())
        self.store.save_settings(
            {
                "baudrate": self.baud_combo.currentText(),
                "last_port": self.port_combo.currentText(),
            }
        )
        self.serial.disconnect()
        event.accept()


def run() -> int:
    """Start the Qt application."""

    app = QApplication(sys.argv)
    from ui.styles import APP_STYLE

    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()
