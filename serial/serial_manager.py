"""Serial communication manager with real and mock MAVLink CLI backends."""

from __future__ import annotations

import logging
import queue
import random
import threading
import time
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal, Slot

try:
    import serial as pyserial
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - handled at runtime for friendlier errors
    pyserial = None
    list_ports = None

try:
    from pymavlink import mavutil
except ImportError:  # pragma: no cover - handled at runtime for friendlier errors
    mavutil = None

from core.cli_parser import MavlinkCliParser
from core.config_schema import PARAMETERS
from core.telemetry_parser import MavlinkTelemetryParser


LOGGER = logging.getLogger(__name__)


class SerialWorker(QObject):
    """Runs blocking serial IO on a background thread."""

    line_received = Signal(str)
    telemetry_received = Signal(dict)
    error = Signal(str)
    info = Signal(str)
    disconnected = Signal()

    def __init__(self, port: str, baudrate: int, mock: bool = False) -> None:
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.mock = mock
        self._running = threading.Event()
        self._tx_queue: queue.Queue[str] = queue.Queue()
        self._serial: Any = None
        self._mavlink: Any = None
        self._text_buffer = bytearray()
        self._mock_config = {param.key: param.default for param in PARAMETERS}
        self._firmware = "MAVLink-CLI FW 1.0.0"
        self._mock_tick = 0

    @Slot()
    def read_loop(self) -> None:
        """Read incoming serial data until stopped."""

        self._running.set()
        if self.mock:
            self._run_mock_loop()
            return

        if pyserial is None:
            self.error.emit("pyserial is not installed.")
            self.disconnected.emit()
            return

        try:
            self._serial = pyserial.Serial(self.port, self.baudrate, timeout=0.1)
            if mavutil is not None:
                self._mavlink = mavutil.mavlink.MAVLink(None)
            else:
                self.info.emit("pymavlink is not installed; MAVLink telemetry is disabled.")
            self.info.emit(f"Connected to {self.port} at {self.baudrate}.")
            while self._running.is_set():
                self._drain_tx_queue()
                chunk = self._serial.read(128)
                if not chunk:
                    continue
                self._handle_serial_chunk(chunk)
        except Exception as exc:
            LOGGER.exception("Serial read loop failed")
            self.error.emit(str(exc))
        finally:
            self._close_serial()
            self.disconnected.emit()

    @Slot(str)
    def send(self, command: str) -> None:
        """Queue a command to be sent by the background worker."""

        self._tx_queue.put(command)

    @Slot()
    def stop(self) -> None:
        """Stop the worker loop."""

        self._running.clear()

    def _drain_tx_queue(self) -> None:
        while self._running.is_set():
            try:
                command = self._tx_queue.get_nowait()
            except queue.Empty:
                break
            try:
                payload = (command.rstrip() + "\r\n").encode("utf-8")
                self._serial.write(payload)
                self._serial.flush()
            except Exception as exc:
                LOGGER.exception("Failed to send serial command")
                self.error.emit(f"TX failed: {exc}")

    def _handle_serial_chunk(self, chunk: bytes) -> None:
        self._parse_mavlink_chunk(chunk)
        self._parse_text_chunk(chunk)

    def _parse_mavlink_chunk(self, chunk: bytes) -> None:
        if self._mavlink is None:
            return

        for byte in chunk:
            try:
                message = self._mavlink.parse_char(bytes((byte,)))
            except Exception as exc:
                LOGGER.debug("MAVLink byte parse failed: %s", exc)
                continue
            if message is None:
                continue
            telemetry = MavlinkTelemetryParser.parse_message(message)
            if telemetry:
                self.telemetry_received.emit(telemetry)

    def _parse_text_chunk(self, chunk: bytes) -> None:
        for byte in chunk:
            if byte in (10, 13):
                self._emit_text_buffer()
                continue
            if byte in (9,) or 32 <= byte <= 126:
                self._text_buffer.append(byte)
                if len(self._text_buffer) > 1024:
                    self._text_buffer.clear()
                continue
            if self._text_buffer:
                self._text_buffer.clear()

    def _emit_text_buffer(self) -> None:
        if not self._text_buffer:
            return
        line = self._text_buffer.decode("utf-8", errors="replace").strip()
        self._text_buffer.clear()
        if line:
            self.line_received.emit(line)

    def _run_mock_loop(self) -> None:
        self.info.emit(f"Mock serial connected at {self.baudrate}.")
        self.line_received.emit(self._firmware)
        last_heartbeat = time.monotonic()
        last_telemetry = time.monotonic()
        while self._running.is_set():
            self._drain_mock_queue()
            now = time.monotonic()
            if now - last_heartbeat > 3:
                self.line_received.emit("HEARTBEAT=OK")
                last_heartbeat = now
            if now - last_telemetry > 1:
                for line in self._mock_telemetry_lines():
                    self.line_received.emit(line)
                    telemetry = MavlinkTelemetryParser.parse_line(line)
                    if telemetry:
                        self.telemetry_received.emit(telemetry)
                last_telemetry = now
            time.sleep(0.05)
        self.disconnected.emit()

    def _drain_mock_queue(self) -> None:
        while self._running.is_set():
            try:
                command = self._tx_queue.get_nowait().strip()
            except queue.Empty:
                break

            if not command:
                continue

            lower = command.lower().rstrip(";")
            if lower in {"dump", "pl"}:
                self.line_received.emit("# BEGIN CONFIG")
                for key, value in self._mock_config.items():
                    self.line_received.emit(f"{key}={MavlinkCliParser.serialize_value(key, value)}")
                    time.sleep(0.015)
                self.line_received.emit("# END CONFIG")
            elif lower.startswith("set "):
                self._handle_mock_set(command[4:])
            elif lower.startswith("p ") and "=" in lower:
                assignment = command[2:].strip().rstrip(";")
                self._handle_mock_set(assignment)
            elif lower in {"save", "pstore"}:
                self.line_received.emit("INFO=Configuration saved")
            elif lower == "reboot":
                self.line_received.emit("INFO=Rebooting module")
                time.sleep(0.25)
                self.line_received.emit(self._firmware)
            elif lower in {"version", "v"}:
                self.line_received.emit(f"FW_VERSION={self._firmware}")
            else:
                self.line_received.emit(f"ECHO={command}")

            if random.random() < 0.08:
                self.line_received.emit(f"RSSI={random.randint(70, 99)}")

    def _mock_telemetry_lines(self) -> list[str]:
        self._mock_tick += 1
        lat = 107769000 + self._mock_tick * 25
        lon = 1067009000 + self._mock_tick * 30
        altitude_mm = 30500 + self._mock_tick * 20
        rc_channels = " ".join(f"chan{channel}_raw={1000 + channel * 35}" for channel in range(1, 19))
        servo_outputs = " ".join(f"servo{servo}_raw={1050 + servo * 40}" for servo in range(1, 17))
        return [
            "HEARTBEAT type=2 autopilot=3 base_mode=81 custom_mode=5 system_status=4 mavlink_version=3",
            (
                "ATTITUDE roll=0.03 pitch=-0.02 yaw=1.57 "
                "rollspeed=0.001 pitchspeed=0.002 yawspeed=0.003"
            ),
            f"GLOBAL_POSITION_INT lat={lat} lon={lon} alt={altitude_mm} relative_alt=10200 vx=45 vy=12 vz=-2 hdg=9000",
            "SYS_STATUS voltage_battery=12150 current_battery=145 battery_remaining=86 drop_rate_comm=0 "
            "load=320 errors_count1=0 errors_count2=0 errors_count3=0 errors_count4=0",
            f"GPS_RAW_INT fix_type=3 lat={lat} lon={lon} alt={altitude_mm} eph=80 epv=120 vel=940 cog=9000 satellites_visible=14",
            f"RC_CHANNELS chancount=18 {rc_channels} rssi=220",
            f"SERVO_OUTPUT_RAW port=0 {servo_outputs}",
            "STATUSTEXT severity=6 text=Mock MAVLink telemetry active",
        ]

    def _handle_mock_set(self, assignment: str) -> None:
        parsed = MavlinkCliParser.parse_line(assignment)
        if parsed is None:
            self.line_received.emit("ERROR=Invalid set command")
            return
        key, value = parsed
        self._mock_config[key] = MavlinkCliParser.normalize_value(key, value)
        self.line_received.emit(f"{key}={MavlinkCliParser.serialize_value(key, self._mock_config[key])}")
        self.line_received.emit("INFO=OK")

    def _close_serial(self) -> None:
        try:
            if self._serial is not None and self._serial.is_open:
                self._serial.close()
        except Exception as exc:
            LOGGER.debug("Serial close failed: %s", exc)


class SerialManager(QObject):
    """High-level serial API used by the GUI."""

    line_received = Signal(str)
    telemetry_received = Signal(dict)
    error = Signal(str)
    info = Signal(str)
    connected_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: SerialWorker | None = None
        self._connected = False

    @staticmethod
    def scan_ports() -> list[str]:
        """Return available serial ports, plus mock mode for hardware-free testing."""

        ports = ["MOCK"]
        if list_ports is None:
            return ports
        try:
            ports.extend(port.device for port in list_ports.comports())
        except Exception as exc:
            LOGGER.warning("Port scan failed: %s", exc)
        return ports

    def connect(self, port: str, baudrate: int) -> None:
        """Connect to a real serial port or mock backend."""

        if self._connected:
            return

        thread = QThread(self)
        worker = SerialWorker(port, baudrate, mock=(port == "MOCK"))
        self._thread = thread
        self._worker = worker

        worker.moveToThread(thread)
        thread.started.connect(worker.read_loop)
        worker.line_received.connect(self.line_received)
        worker.telemetry_received.connect(self.telemetry_received)
        worker.error.connect(self.error)
        worker.info.connect(self.info)
        worker.disconnected.connect(self._handle_disconnected)
        worker.disconnected.connect(thread.quit)
        worker.disconnected.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._handle_thread_finished)
        thread.start()
        self._connected = True
        self.connected_changed.emit(True)

    def disconnect(self) -> None:
        """Disconnect without blocking the GUI thread."""

        if self._worker is not None:
            self._worker.stop()

    def send(self, command: str) -> None:
        """Send a CLI command to the active backend."""

        if not self._connected or self._worker is None:
            self.error.emit("Not connected.")
            return
        self._worker.send(command)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @Slot()
    def _handle_disconnected(self) -> None:
        self._connected = False
        self.connected_changed.emit(False)

    @Slot()
    def _handle_thread_finished(self) -> None:
        self._worker = None
        self._thread = None
