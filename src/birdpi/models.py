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
