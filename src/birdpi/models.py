from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class DetectedObject:
    """
    Represent one detected object within an image.
    """

    label: str
    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True, slots=True)
class CapturedImage:
    """
    Represent a captured BirdPi image.
    """

    path: Path
    captured_at: datetime
    session_id: str | None = None

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
class MotionEvent:
    """
    Represent one motion-triggered wildlife event.
    """

    id: str
    started_at: datetime
    ended_at: datetime | None = None
    images: list[CapturedImage] = field(default_factory=list)
    video_filename: str | None = None

    @property
    def active(self) -> bool:
        return self.ended_at is None

    def add_image(
            self,
            image: CapturedImage,
    ) -> None:
        self.images.append(image)

    def close(
            self,
            ended_at: datetime | None = None,
    ) -> None:
        self.ended_at = ended_at or datetime.now()
