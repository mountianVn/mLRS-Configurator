"""Realtime MAVLink telemetry dashboard widget."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget


class TelemetryWidget(QWidget):
    """Displays MAVLink telemetry values from selected message types."""

    ROWS: tuple[tuple[str, str], ...] = (
        ("HEARTBEAT", "FC Status"),
        ("HEARTBEAT", "Flight Mode"),
        ("HEARTBEAT", "MAV Type"),
        ("HEARTBEAT", "Autopilot"),
        ("HEARTBEAT", "Base Mode"),
        ("HEARTBEAT", "MAVLink Version"),
        ("ATTITUDE", "Roll"),
        ("ATTITUDE", "Pitch"),
        ("ATTITUDE", "Yaw"),
        ("ATTITUDE", "Roll Speed"),
        ("ATTITUDE", "Pitch Speed"),
        ("ATTITUDE", "Yaw Speed"),
        ("GLOBAL_POSITION_INT", "Latitude"),
        ("GLOBAL_POSITION_INT", "Longitude"),
        ("GLOBAL_POSITION_INT", "GPS Altitude"),
        ("GLOBAL_POSITION_INT", "Relative Altitude"),
        ("GLOBAL_POSITION_INT", "GPS Heading"),
        ("GLOBAL_POSITION_INT", "Velocity X"),
        ("GLOBAL_POSITION_INT", "Velocity Y"),
        ("GLOBAL_POSITION_INT", "Velocity Z"),
        ("SYS_STATUS", "Battery Voltage"),
        ("SYS_STATUS", "Battery Current"),
        ("SYS_STATUS", "Battery Remaining"),
        ("SYS_STATUS", "Drop Rate"),
        ("SYS_STATUS", "Load"),
        ("SYS_STATUS", "Error Count 1"),
        ("SYS_STATUS", "Error Count 2"),
        ("SYS_STATUS", "Error Count 3"),
        ("SYS_STATUS", "Error Count 4"),
        ("GPS_RAW_INT", "GPS Fix Type"),
        ("GPS_RAW_INT", "GPS Satellites"),
        ("GPS_RAW_INT", "GPS Raw Latitude"),
        ("GPS_RAW_INT", "GPS Raw Longitude"),
        ("GPS_RAW_INT", "GPS Raw Altitude"),
        ("GPS_RAW_INT", "GPS EPH"),
        ("GPS_RAW_INT", "GPS EPV"),
        ("GPS_RAW_INT", "GPS Velocity"),
        ("GPS_RAW_INT", "GPS COG"),
        ("RC_CHANNELS", "RC Channel Count"),
        ("RC_CHANNELS", "RC RSSI"),
        *((("RC_CHANNELS", f"RC CH{channel}") for channel in range(1, 19))),
        ("SERVO_OUTPUT_RAW", "Servo Port"),
        *((("SERVO_OUTPUT_RAW", f"Servo {servo}") for servo in range(1, 17))),
        ("STATUSTEXT", "Status Severity"),
        ("STATUSTEXT", "Status Text"),
    )

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("telemetryPanel")
        self.setMaximumHeight(360)
        self._labels: dict[str, QLabel] = {}

        title = QLabel("MAVLink Telemetry")
        title.setObjectName("sectionTitle")

        body = QWidget()
        grid = QGridLayout(body)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(7)

        current_group = ""
        row = 0
        for group, name in self.ROWS:
            if group != current_group:
                group_label = QLabel(group)
                group_label.setObjectName("telemetryGroup")
                grid.addWidget(group_label, row, 0, 1, 2)
                row += 1
                current_group = group

            name_label = QLabel(name)
            name_label.setObjectName("telemetryName")
            value_label = QLabel("--")
            value_label.setObjectName("telemetryValue")
            value_label.setWordWrap(True)
            grid.addWidget(name_label, row, 0)
            grid.addWidget(value_label, row, 1)
            self._labels[name] = value_label
            row += 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)

    def update_data(self, data: dict[str, str | int | float]) -> None:
        """Update telemetry labels from parsed MAVLink values."""

        for key, value in data.items():
            label = self._labels.get(key)
            if label is not None:
                label.setText(str(value))
