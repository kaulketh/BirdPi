"""
Logging configuration for BirdPi.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = (
    "%(asctime)s "
    "%(levelname)-8s "
    "%(name)s: "
    "%(message)s"
)


def configure_logging(
        log_file: Path,
        level: int = logging.INFO,
        max_bytes: int = 5_000_000,
        backup_count: int = 3,
) -> None:
    """
    Configure BirdPi logging.

    Logs are written both to stdout and to a rotating logfile.
    """

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        _LOG_FORMAT
    )

    # Avoid adding a second console handler.
    if not any(
            isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, RotatingFileHandler)
            for handler in root_logger.handlers
    ):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        root_logger.addHandler(
            console_handler
        )

    # Avoid adding the same logfile twice.
    log_file = log_file.resolve()

    if not any(
            isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename).resolve() == log_file
            for handler in root_logger.handlers
    ):
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        root_logger.addHandler(
            file_handler
        )


def get_logger(
        name: str,
) -> logging.Logger:
    """
    Return a named logger.
    """

    return logging.getLogger(name)
