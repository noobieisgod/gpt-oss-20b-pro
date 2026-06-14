from __future__ import annotations

import logging


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
