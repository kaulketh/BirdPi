"""
Logging configuration for BirdPi.
"""

import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s"
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
