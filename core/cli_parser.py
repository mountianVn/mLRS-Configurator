"""Parser and command builder for text based module CLI communication."""

from __future__ import annotations

import logging
import re
from typing import Any

from core.config_schema import CANONICAL_KEY_MAP, PARAMETERS, PARAMETER_MAP


LOGGER = logging.getLogger(__name__)


class MavlinkCliParser:
    """Converts module CLI text into config dictionaries and builds commands."""

    READ_COMMAND = "pl;"
    SAVE_COMMAND = "pstore;"
    VERSION_COMMAND = "v;"
    REBOOT_COMMAND = "reboot;"
    KEY_VALUE_RE = re.compile(r"^\s*(?:p\s+)?([A-Za-z0-9_]+)\s*=\s*(.*?)\s*;?\s*$", re.IGNORECASE)
    DISPLAY_VALUE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 _/-]*?)\s*=\s*(.*?)\s*;?\s*$")
    LOG_PREFIX_RE = re.compile(r"^\s*(?:\[[^\]]+\]\s*)?(?:RX|TX|INFO|ERROR):\s*", re.IGNORECASE)
    BRACKET_VALUE_RE = re.compile(r"\[([^\]]+)\]\s*(?:\([^)]*\))?\s*$")
    UNAVAILABLE_RE = re.compile(r"\bunavailable\b", re.IGNORECASE)
    LABEL_ALIASES = {
        "ch source": "tx_ch_source",
        "out lq ch": "RX_OUT_LQ_CH",
        "out mode": "RX_OUT_MODE",
        "out rssi ch": "RX_OUT_RSSI_CH",
        "power sw ch": "rx_power_sw_ch",
        "ser baudrate": "rx_ser_baudrate",
        "ser link mode": "RX_SER_LINK_MODE",
        "ser port": "Rx_Ser_Port",
        "snd radio stat": "Rx_Snd_RadioStat",
        "snd radiostat": "Rx_Snd_RadioStat",
        "snd rcchannel": "RX_SND_RCCHANNEL",
        "tx ch source": "tx_ch_source",
        "tx ch order": "tx_ch_order",
        "tx power": "tx_power",
        "tx power sw ch": "tx_power_sw_ch",
        "tx ser baudrate": "tx_ser_baudrate",
        "tx ser dest": "tx_ser_dest",
        "tx snd radiostat": "tx_snd_radiostat",
        "tx mav component": "TX_MAV_COMPONENT",
        "rx out lq ch": "RX_OUT_LQ_CH",
        "rx out mode": "RX_OUT_MODE",
        "rx out rssi ch": "RX_OUT_RSSI_CH",
        "rx power sw ch": "rx_power_sw_ch",
        "rx ser baudrate": "rx_ser_baudrate",
        "rx ser link mode": "RX_SER_LINK_MODE",
        "rx ser port": "Rx_Ser_Port",
        "rx snd radio stat": "Rx_Snd_RadioStat",
        "rx snd radiostat": "Rx_Snd_RadioStat",
        "rx snd rcchannel": "RX_SND_RCCHANNEL",
    }
    LABEL_KEY_MAP = {
        **{param.label.strip().lower(): param.key for param in PARAMETERS},
        **LABEL_ALIASES,
    }

    @classmethod
    def parse_line(cls, line: str) -> tuple[str, str] | None:
        """Parse a single ``KEY=VALUE`` line.

        Non key-value status lines are ignored by returning ``None``.
        """

        clean_line = cls.LOG_PREFIX_RE.sub("", line.strip())
        match = cls.KEY_VALUE_RE.match(clean_line)
        if not match:
            match = cls.DISPLAY_VALUE_RE.match(clean_line)
        if not match:
            return None
        key, value = match.groups()
        clean_key = key.strip()
        canonical_key = cls._canonical_key(clean_key)
        return canonical_key, value.strip()

    @classmethod
    def parse_dump(cls, text: str) -> dict[str, Any]:
        """Parse a multiline CLI dump into normalized parameter values."""

        config: dict[str, Any] = {}
        for raw_line in text.splitlines():
            parsed = cls.parse_line(raw_line)
            if parsed is None:
                continue
            key, value = parsed
            if cls.UNAVAILABLE_RE.search(str(value)):
                continue
            if key in PARAMETER_MAP:
                config[key] = cls.normalize_value(key, value)
            else:
                LOGGER.debug("Ignoring unknown CLI key %s", key)
        return config

    @classmethod
    def normalize_value(cls, key: str, value: Any) -> Any:
        """Convert raw CLI strings into the widget value expected by the UI."""

        param = PARAMETER_MAP.get(key)
        if param is None:
            return value

        if param.field_type == "bool":
            return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled"}

        if param.field_type == "enum":
            text, bracket_value = cls._split_display_value(str(value))
            if param.option_values:
                if bracket_value:
                    for label, cli_value in param.option_values.items():
                        if bracket_value.lower() == cli_value.lower():
                            return label
                for label, cli_value in param.option_values.items():
                    if text.lower() == cli_value.lower() or text.lower() == label.lower():
                        return label
                    if cls._normalize_token(label) and cls._normalize_token(label) in cls._normalize_token(text):
                        return label
                    if cls._label_channel(label) == text:
                        return label
            return text

        if param.field_type == "int":
            try:
                text, bracket_value = cls._split_display_value(str(value))
                candidate = bracket_value if bracket_value and cls._is_number(bracket_value) else text
                match = re.search(r"-?\d+(?:\.\d+)?", candidate)
                if match is None:
                    raise ValueError
                return int(float(match.group(0)))
            except ValueError:
                return param.default

        if param.field_type == "float":
            try:
                text, bracket_value = cls._split_display_value(str(value))
                candidate = bracket_value if bracket_value and cls._is_number(bracket_value) else text
                match = re.search(r"-?\d+(?:\.\d+)?", candidate)
                if match is None:
                    raise ValueError
                return float(match.group(0))
            except ValueError:
                return param.default

        return cls._split_display_value(str(value))[0]

    @classmethod
    def serialize_value(cls, key: str, value: Any) -> str:
        """Convert a UI value into a CLI-safe string."""

        param = PARAMETER_MAP.get(key)
        if param is None:
            return str(value)

        if param.field_type == "bool":
            return "1" if bool(value) else "0"

        if param.field_type == "enum" and param.option_values:
            return param.option_values.get(str(value), str(value))

        if param.field_type == "float":
            return f"{float(value):g}"

        return str(value)

    @classmethod
    def build_set_command(cls, key: str, value: Any) -> str:
        """Build a module CLI set command."""

        return f"p {key}={cls.serialize_value(key, value)};"

    @classmethod
    def _canonical_key(cls, key: str) -> str:
        lower_key = key.lower()
        canonical_key = CANONICAL_KEY_MAP.get(lower_key)
        if canonical_key is not None:
            return canonical_key
        return cls.LABEL_KEY_MAP.get(lower_key, key)

    @classmethod
    def _split_display_value(cls, value: str) -> tuple[str, str | None]:
        text = value.strip().rstrip(";").strip()
        bracket_value = None
        bracket_match = cls.BRACKET_VALUE_RE.search(text)
        if bracket_match:
            bracket_value = bracket_match.group(1).strip()
            text = text[: bracket_match.start()].strip()
        text = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
        return text, bracket_value

    @staticmethod
    def _normalize_token(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    @staticmethod
    def _label_channel(label: str) -> str | None:
        match = re.search(r"\bch\s*(\d+)\b", label, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _is_number(value: str) -> bool:
        try:
            float(value)
        except ValueError:
            return False
        return True
