"""
This module defines the structure and functionality for working with a captured BirdPi image.

The module provides a data class to represent an image, capturing its metadata such as file
path, timestamp, and size in various units.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CapturedImage:
    """
    Represent a captured BirdPi image.
    """

    path: Path
    captured_at: datetime

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def size_bytes(self) -> int:
        return self.path.stat().st_size

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)


@dataclass(slots=True)
class ObservationSession:
    """
    Represent a BirdPi observation session.
    """

    started_at: datetime
    stopped_at: datetime | None = None
    capture_count: int = 0

    @property
    def active(self) -> bool:
        return self.stopped_at is None
