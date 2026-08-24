from dataclasses import dataclass, field
from datetime import datetime
from datetime import timedelta
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

    @property
    def duration(self) -> timedelta:
        end = self.stopped_at or datetime.now()
        return end - self.started_at

    @property
    def duration_text(self) -> str:
        """
        Return session duration formatted as HH:MM:SS.
        """

        total_seconds = int(self.duration.total_seconds())

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def id(self) -> str:
        return self.started_at.strftime("%Y%m%d_%H%M%S")


@dataclass(slots=True)
class Observation:
    """
    Represent a detected observation in a captured image.
    """

    image: CapturedImage
    detected_at: datetime

    detection_label: str
    detection_confidence: float

    objects: list[DetectedObject] = field(default_factory=list)

    classification_label: str | None = None
    classification_confidence: float | None = None

    @property
    def id(self) -> str:
        """
        Return the unique observation identifier.
        """

        return self.detected_at.strftime("%Y%m%d_%H%M%S_%f")


@dataclass(slots=True)
class MotionEvent:
    """
    Represent one motion-triggered wildlife event.
    """

    id: str
    started_at: datetime
    ended_at: datetime | None = None
    images: list[CapturedImage] = field(default_factory=list)

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
