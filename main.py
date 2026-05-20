"""Entry point for the MAVLink CLI Configurator."""

from __future__ import annotations

import logging
import sys

from ui.main_window import run


def configure_logging() -> None:
    """Configure application-wide logging for troubleshooting."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


if __name__ == "__main__":
    configure_logging()
    sys.exit(run())
