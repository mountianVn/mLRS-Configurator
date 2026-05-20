"""JSON persistence helpers for local app settings and config snapshots."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)
APP_DIR = Path.home() / ".mavlink_cli_configurator"
LOCAL_CONFIG_PATH = APP_DIR / "last_config.json"
SETTINGS_PATH = APP_DIR / "settings.json"


class ConfigStore:
    """Stores recent module configuration and UI preferences as JSON."""

    def __init__(self, config_path: Path = LOCAL_CONFIG_PATH, settings_path: Path = SETTINGS_PATH) -> None:
        self.config_path = config_path
        self.settings_path = settings_path

    def load_config(self) -> dict[str, Any]:
        """Load the last known module configuration."""

        return self._read_json(self.config_path)

    def save_config(self, config: dict[str, Any]) -> None:
        """Persist the last known module configuration."""

        self._write_json(self.config_path, config)

    def load_settings(self) -> dict[str, Any]:
        """Load UI settings such as selected baudrate and mock mode."""

        return self._read_json(self.settings_path)

    def save_settings(self, settings: dict[str, Any]) -> None:
        """Persist UI settings."""

        self._write_json(self.settings_path, settings)

    @staticmethod
    def import_config(path: str | Path) -> dict[str, Any]:
        """Read a config snapshot from a user-selected JSON file."""

        with Path(path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("Config JSON must contain an object.")
        return data

    @staticmethod
    def export_config(path: str | Path, config: dict[str, Any]) -> None:
        """Write a config snapshot to a user-selected JSON file."""

        target = Path(path)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, sort_keys=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            LOGGER.warning("Failed to read %s: %s", path, exc)
            return {}
        return data if isinstance(data, dict) else {}

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
        except OSError as exc:
            LOGGER.warning("Failed to write %s: %s", path, exc)
