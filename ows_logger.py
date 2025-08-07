import logging
import sys
import os

try:
    from systemd.journal import JournalHandler
    SYSTEMD_AVAILABLE = True
except ImportError:
    SYSTEMD_AVAILABLE = False


def setup_logger(name: str = "myapp", debug: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False  # Avoid double logging if root logger is used

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if debug or not SYSTEMD_AVAILABLE:
        # Console handler for debugging or fallback
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    else:
        # Systemd journal handler
        handler = JournalHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    logger.addHandler(handler)
    return logger
