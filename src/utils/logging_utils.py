"""Minimal logging setup for the project."""
import logging
from typing import Optional


def setup_logging(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger with a standard format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
