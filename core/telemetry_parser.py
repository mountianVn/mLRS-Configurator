"""Parser for text-form MAVLink telemetry lines."""

from __future__ import annotations

import re

try:
    from pymavlink import mavutil
except ImportError:  # pragma: no cover - runtime dependency is optional for text-only parsing
    mavutil = None


class MavlinkTelemetryParser:
    """Parses MAVLink message text into UI telemetry fields.

    The serial CLI is text based, so this parser accepts practical formats such as:
    ``HEARTBEAT base_mode=81 custom_mode=4 system_status=4``,
    ``ATTITUDE: roll=0.1 pitch=-0.2 yaw=1.57``, or comma separated variants.
    """

    MESSAGE_NAMES = (
        "HEARTBEAT",
        "ATTITUDE",
        "GLOBAL_POSITION_INT",
        "SYS_STATUS",
        "GPS_RAW_INT",
        "RC_CHANNELS",
        "SERVO_OUTPUT_RAW",
        "STATUSTEXT",
    )
    TOKEN_RE = re.compile(r"([A-Za-z0-9_]+)\s*=\s*([^,\s;]+)")
    MAV_TYPE_NAMES = {
        0: "Generic",
        1: "Fixed Wing",
        2: "Quadrotor",
        3: "Coaxial",
        4: "Helicopter",
        10: "Ground Rover",
        12: "Submarine",
        13: "Hexarotor",
        14: "Octorotor",
        15: "Tricopter",
        19: "VTOL Quadrotor",
        27: "Battery",
        29: "Onboard Controller",
    }
    AUTOPILOT_NAMES = {
        0: "Generic",
        3: "ArduPilotMega",
        8: "ArduPilotMega",
        12: "PX4",
    }
    MAV_STATE_NAMES = {
        0: "Uninitialized",
        1: "Boot",
        2: "Calibrating",
        3: "Standby",
        4: "Active",
        5: "Critical",
        6: "Emergency",
        7: "Poweroff",
        8: "Flight Termination",
    }
    BASE_MODE_FLAGS = {
        128: "Armed",
        64: "Manual Input",
        32: "HIL",
        16: "Stabilize",
        8: "Guided",
        4: "Auto",
        2: "Test",
        1: "Custom Mode",
    }
    ARDUPILOT_COPTER_MODES = {
        0: "Stabilize",
        1: "Acro",
        2: "AltHold",
        3: "Auto",
        4: "Guided",
        5: "Loiter",
        6: "RTL",
        7: "Circle",
        9: "Land",
        11: "Drift",
        13: "Sport",
        14: "Flip",
        15: "AutoTune",
        16: "PosHold",
        17: "Brake",
        18: "Throw",
        19: "Avoid ADSB",
        20: "Guided NoGPS",
        21: "Smart RTL",
        22: "FlowHold",
        23: "Follow",
        24: "ZigZag",
        25: "SystemID",
        26: "Auto RTL",
        27: "Auto Rotate",
        28: "Turtle",
    }

    @classmethod
    def parse_line(cls, line: str) -> dict[str, str]:
        """Parse one telemetry line into display labels and values."""

        message_name = cls._message_name(line)
        if message_name is None:
            return {}

        values = cls._values(line)
        if message_name == "HEARTBEAT":
            return cls._parse_heartbeat(values)
        if message_name == "ATTITUDE":
            return cls._parse_attitude(values)
        if message_name == "GLOBAL_POSITION_INT":
            return cls._parse_global_position(values)
        if message_name == "SYS_STATUS":
            return cls._parse_sys_status(values)
        if message_name == "GPS_RAW_INT":
            return cls._parse_gps_raw(values)
        if message_name == "RC_CHANNELS":
            return cls._parse_rc_channels(values)
        if message_name == "SERVO_OUTPUT_RAW":
            return cls._parse_servo_output(values)
        if message_name == "STATUSTEXT":
            return cls._parse_status_text(values)
        return {}

    @classmethod
    def parse_message(cls, message: object) -> dict[str, str]:
        """Parse one pymavlink MAVLink_message into display labels and values."""

        get_type = getattr(message, "get_type", None)
        to_dict = getattr(message, "to_dict", None)
        if get_type is None or to_dict is None:
            return {}

        message_name = str(get_type()).upper()
        if message_name not in cls.MESSAGE_NAMES:
            return {}

        values = {str(key).lower(): str(value) for key, value in to_dict().items()}
        if message_name == "HEARTBEAT":
            return cls._parse_heartbeat(values)
        if message_name == "ATTITUDE":
            return cls._parse_attitude(values)
        if message_name == "GLOBAL_POSITION_INT":
            return cls._parse_global_position(values)
        if message_name == "SYS_STATUS":
            return cls._parse_sys_status(values)
        if message_name == "GPS_RAW_INT":
            return cls._parse_gps_raw(values)
        if message_name == "RC_CHANNELS":
            return cls._parse_rc_channels(values)
        if message_name == "SERVO_OUTPUT_RAW":
            return cls._parse_servo_output(values)
        if message_name == "STATUSTEXT":
            return cls._parse_status_text(values)
        return {}

    @classmethod
    def _message_name(cls, line: str) -> str | None:
        upper_line = line.upper()
        for name in cls.MESSAGE_NAMES:
            if upper_line.startswith(name) or upper_line.startswith(f"{name}:") or upper_line.startswith(f"{name},"):
                return name
        return None

    @classmethod
    def _values(cls, line: str) -> dict[str, str]:
        values = {key.lower(): value for key, value in cls.TOKEN_RE.findall(line)}
        if cls._message_name(line) == "STATUSTEXT":
            match = re.search(r"\btext\s*=\s*(.+?)\s*;?\s*$", line, re.IGNORECASE)
            if match:
                values["text"] = match.group(1).strip()
        return values

    @staticmethod
    def _get(values: dict[str, str], *keys: str, default: str = "--") -> str:
        for key in keys:
            value = values.get(key.lower())
            if value is not None:
                return value
        return default

    @classmethod
    def _parse_heartbeat(cls, values: dict[str, str]) -> dict[str, str]:
        mav_type = cls._get(values, "type", "mav_type")
        autopilot = cls._get(values, "autopilot")
        base_mode = cls._get(values, "base_mode")
        custom_mode = cls._get(values, "custom_mode", "mode", "flight_mode")
        return {
            "FC Status": cls._format_enum(cls._get(values, "system_status", "status", "state"), cls.MAV_STATE_NAMES),
            "Flight Mode": cls._format_flight_mode(custom_mode, mav_type, autopilot),
            "MAV Type": cls._format_enum(mav_type, cls.MAV_TYPE_NAMES),
            "Autopilot": cls._format_enum(autopilot, cls.AUTOPILOT_NAMES),
            "Base Mode": cls._format_base_mode(base_mode),
            "MAVLink Version": cls._get(values, "mavlink_version"),
        }

    @classmethod
    def _parse_attitude(cls, values: dict[str, str]) -> dict[str, str]:
        return {
            "Roll": cls._format_float(cls._get(values, "roll"), "rad"),
            "Pitch": cls._format_float(cls._get(values, "pitch"), "rad"),
            "Yaw": cls._format_float(cls._get(values, "yaw"), "rad"),
            "Roll Speed": cls._format_float(cls._get(values, "rollspeed", "roll_speed"), "rad/s"),
            "Pitch Speed": cls._format_float(cls._get(values, "pitchspeed", "pitch_speed"), "rad/s"),
            "Yaw Speed": cls._format_float(cls._get(values, "yawspeed", "yaw_speed"), "rad/s"),
        }

    @classmethod
    def _parse_global_position(cls, values: dict[str, str]) -> dict[str, str]:
        return {
            "Latitude": cls._format_scaled_degrees(cls._get(values, "lat", "latitude")),
            "Longitude": cls._format_scaled_degrees(cls._get(values, "lon", "lng", "longitude")),
            "GPS Altitude": cls._format_scaled_mm(cls._get(values, "alt", "altitude")),
            "Relative Altitude": cls._format_scaled_mm(cls._get(values, "relative_alt", "relative_altitude")),
            "GPS Heading": cls._format_heading(cls._get(values, "hdg", "heading")),
            "Velocity X": cls._format_centimeters_per_second(cls._get(values, "vx")),
            "Velocity Y": cls._format_centimeters_per_second(cls._get(values, "vy")),
            "Velocity Z": cls._format_centimeters_per_second(cls._get(values, "vz")),
        }

    @classmethod
    def _parse_sys_status(cls, values: dict[str, str]) -> dict[str, str]:
        return {
            "Battery Voltage": cls._format_voltage(cls._get(values, "voltage_battery", "voltage")),
            "Battery Current": cls._format_current(cls._get(values, "current_battery", "current")),
            "Battery Remaining": cls._format_percent(cls._get(values, "battery_remaining", "remaining")),
            "Drop Rate": cls._format_tenths_percent(cls._get(values, "drop_rate_comm", "drop_rate")),
            "Error Count 1": cls._get(values, "errors_count1"),
            "Error Count 2": cls._get(values, "errors_count2"),
            "Error Count 3": cls._get(values, "errors_count3"),
            "Error Count 4": cls._get(values, "errors_count4"),
            "Load": cls._format_tenths_percent(cls._get(values, "load")),
        }

    @classmethod
    def _parse_gps_raw(cls, values: dict[str, str]) -> dict[str, str]:
        return {
            "GPS Fix Type": cls._get(values, "fix_type"),
            "GPS Satellites": cls._get(values, "satellites_visible"),
            "GPS Raw Latitude": cls._format_scaled_degrees(cls._get(values, "lat")),
            "GPS Raw Longitude": cls._format_scaled_degrees(cls._get(values, "lon")),
            "GPS Raw Altitude": cls._format_scaled_mm(cls._get(values, "alt")),
            "GPS EPH": cls._get(values, "eph"),
            "GPS EPV": cls._get(values, "epv"),
            "GPS Velocity": cls._format_centimeters_per_second(cls._get(values, "vel")),
            "GPS COG": cls._format_heading(cls._get(values, "cog")),
        }

    @classmethod
    def _parse_rc_channels(cls, values: dict[str, str]) -> dict[str, str]:
        parsed = {
            "RC Channel Count": cls._get(values, "chancount"),
            "RC RSSI": cls._format_rc_rssi(cls._get(values, "rssi")),
        }
        for channel in range(1, 19):
            parsed[f"RC CH{channel}"] = cls._format_pwm(cls._get(values, f"chan{channel}_raw"))
        return parsed

    @classmethod
    def _parse_servo_output(cls, values: dict[str, str]) -> dict[str, str]:
        parsed = {"Servo Port": cls._get(values, "port")}
        for servo in range(1, 17):
            parsed[f"Servo {servo}"] = cls._format_pwm(cls._get(values, f"servo{servo}_raw"))
        return parsed

    @classmethod
    def _parse_status_text(cls, values: dict[str, str]) -> dict[str, str]:
        return {
            "Status Severity": cls._get(values, "severity"),
            "Status Text": cls._get(values, "text"),
        }

    @staticmethod
    def _format_float(value: str, unit: str = "") -> str:
        if value == "--":
            return value
        try:
            text = f"{float(value):.3f}".rstrip("0").rstrip(".")
        except ValueError:
            text = value
        return f"{text} {unit}".strip()

    @staticmethod
    def _format_scaled_degrees(value: str) -> str:
        if value == "--":
            return value
        try:
            numeric = float(value)
            if abs(numeric) > 180:
                numeric /= 1e7
            return f"{numeric:.7f}"
        except ValueError:
            return value

    @staticmethod
    def _format_scaled_mm(value: str) -> str:
        if value == "--":
            return value
        try:
            numeric = float(value)
            if abs(numeric) > 1000:
                numeric /= 1000
            return f"{numeric:.2f} m"
        except ValueError:
            return value

    @staticmethod
    def _format_voltage(value: str) -> str:
        if value == "--":
            return value
        try:
            numeric = float(value)
            if numeric > 100:
                numeric /= 1000
            return f"{numeric:.2f} V"
        except ValueError:
            return value

    @staticmethod
    def _format_current(value: str) -> str:
        if value == "--":
            return value
        try:
            numeric = float(value)
            if abs(numeric) > 100:
                numeric /= 100
            return f"{numeric:.2f} A"
        except ValueError:
            return value

    @staticmethod
    def _format_percent(value: str) -> str:
        if value == "--":
            return value
        return value if value.endswith("%") else f"{value}%"

    @staticmethod
    def _format_tenths_percent(value: str) -> str:
        if value == "--":
            return value
        try:
            return f"{float(value) / 10:.1f}%"
        except ValueError:
            return value

    @staticmethod
    def _format_centimeters_per_second(value: str) -> str:
        if value == "--":
            return value
        try:
            return f"{float(value) / 100:.2f} m/s"
        except ValueError:
            return value

    @staticmethod
    def _format_pwm(value: str) -> str:
        if value == "--":
            return value
        return f"{value} us"

    @staticmethod
    def _format_rc_rssi(value: str) -> str:
        if value == "--" or value == "255":
            return value
        try:
            return f"{float(value) / 254 * 100:.0f}%"
        except ValueError:
            return value

    @classmethod
    def _format_flight_mode(cls, value: str, mav_type: str, autopilot: str) -> str:
        mode_id = cls._to_int(value)
        if mode_id is None:
            return value

        if cls._to_int(autopilot) in {3, 8} and cls._to_int(mav_type) in {0, 2, 13, 14, 15, 19}:
            mode_name = cls.ARDUPILOT_COPTER_MODES.get(mode_id)
            if mode_name is not None:
                return f"{mode_name} ({mode_id})"
        return str(mode_id)

    @classmethod
    def _format_base_mode(cls, value: str) -> str:
        mode = cls._to_int(value)
        if mode is None:
            return value
        flags = [label for bit, label in cls.BASE_MODE_FLAGS.items() if mode & bit]
        if not flags:
            return f"{mode}"
        return f"{', '.join(flags)} ({mode})"

    @classmethod
    def _format_enum(cls, value: str, mapping: dict[int, str]) -> str:
        numeric = cls._to_int(value)
        if numeric is None:
            return value

        name = mapping.get(numeric)
        if name is not None:
            return f"{name} ({numeric})"

        if mavutil is not None:
            name = cls._mavutil_enum_name(value, mapping)
            if name is not None:
                return f"{name} ({numeric})"

        return str(numeric)

    @staticmethod
    def _mavutil_enum_name(value: str, fallback_mapping: dict[int, str]) -> str | None:
        if mavutil is None:
            return None
        numeric = MavlinkTelemetryParser._to_int(value)
        if numeric is None:
            return None
        enum_names = {
            id(MavlinkTelemetryParser.MAV_TYPE_NAMES): "MAV_TYPE",
            id(MavlinkTelemetryParser.AUTOPILOT_NAMES): "MAV_AUTOPILOT",
            id(MavlinkTelemetryParser.MAV_STATE_NAMES): "MAV_STATE",
        }
        enum_name = enum_names.get(id(fallback_mapping))
        if enum_name is None:
            return None
        entry = getattr(mavutil.mavlink, "enums", {}).get(enum_name, {}).get(numeric)
        if entry is None:
            return None
        return str(getattr(entry, "name", "")).removeprefix(f"{enum_name}_").replace("_", " ").title()

    @staticmethod
    def _to_int(value: str) -> int | None:
        try:
            return int(float(value))
        except ValueError:
            return None

    @staticmethod
    def _format_heading(value: str) -> str:
        if value == "--":
            return value
        try:
            numeric = float(value)
            if numeric > 360:
                numeric /= 100
            return f"{numeric:.1f} deg"
        except ValueError:
            return value
