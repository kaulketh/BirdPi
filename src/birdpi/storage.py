"""
A module to handle BirdPi file storage operations.

This module provides the `Storage` class, which offers functionalities for
managing directories, images, observation sessions, and their metadata
in the BirdPi application.

Classes:
    Storage: A class for handling files, directories, and metadata related to BirdPi.
"""
import json
from datetime import datetime
from pathlib import Path

from birdpi.config import Config
from birdpi.models import CapturedImage
from birdpi.models import Observation
from birdpi.models import ObservationSession
from birdpi.models import DetectedObject


class Storage:
    """
    Manage BirdPi file storage.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def ensure_directories(self) -> None:
        """
        Create required directories if they do not exist.
        """

        self.config.image_path.mkdir(
            parents=True,
            exist_ok=True
        )
        self.config.session_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config.observation_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def next_image_path(self, filename: str | None = None) -> Path:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.jpg"

        return self.config.image_path / filename

    def latest_image(self) -> Path | None:
        """
        Return the most recently created image.

        Returns:
            Path of the latest image, or None if no images exist.
        """
        images = sorted(
            self.config.image_path.glob("*.jpg"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        return images[0] if images else None

    def image_count(self) -> int:
        """
        Return the number of stored images.
        """

        return sum(1 for _ in self.config.image_path.glob("*.jpg"))

    def images(self) -> list[CapturedImage]:
        """
        Return all stored images ordered from newest to oldest.
        """

        paths = sorted(
            self.config.image_path.glob("*.jpg"),
            reverse=True,
        )

        return [self.image_from_path(path) for path in paths]

    @staticmethod
    def image_from_path(
            path: Path,
    ) -> CapturedImage:
        """
        Create a CapturedImage from an image path.
        """

        metadata = Storage._load_image_metadata(path)

        captured_at = (
            datetime.fromisoformat(metadata["captured_at"])
            if "captured_at" in metadata
            else datetime.strptime(
                path.stem,
                "image_%Y%m%d_%H%M%S",
            )
        )

        return CapturedImage(
            path=path,
            captured_at=captured_at,
            session_id=metadata.get("session_id"),
        )

    def get_image(self, filename: str) -> CapturedImage | None:
        """
        Return a captured image by filename.
        """

        path = self.config.image_path / filename

        if not path.is_file():
            return None

        return self.image_from_path(path)

    def adjacent_images(
            self,
            image: CapturedImage,
    ) -> tuple[CapturedImage | None, CapturedImage | None]:
        """
        Return the newer and older neighboring images.
        """

        images = self.images()

        try:
            index = images.index(image)
        except ValueError:
            return None, None

        newer = images[index - 1] if index > 0 else None
        older = images[index + 1] if index < len(images) - 1 else None

        return newer, older

    def save_session(
            self,
            session: ObservationSession,
    ) -> Path:
        """
        Persist an observation session as JSON.

        Returns:
            Path of the created session file.
        """

        filename = (
                session.started_at.strftime("%Y%m%d_%H%M%S")
                + ".json"
        )

        output_file = self.config.session_path / filename

        data = {
            "started_at": session.started_at.isoformat(),
            "stopped_at": (
                session.stopped_at.isoformat()
                if session.stopped_at
                else None
            ),
            "capture_count": session.capture_count,
        }

        with output_file.open(
                "w",
                encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
            )

        return output_file

    @staticmethod
    def _session_from_path(
            path: Path,
    ) -> ObservationSession:
        """
        Create an ObservationSession from a JSON file.
        """

        with path.open(
                "r",
                encoding="utf-8",
        ) as file:
            data = json.load(file)

        return ObservationSession(
            started_at=datetime.fromisoformat(
                data["started_at"]
            ),
            stopped_at=(
                datetime.fromisoformat(data["stopped_at"])
                if data["stopped_at"]
                else None
            ),
            capture_count=data["capture_count"],
        )

    def sessions(self) -> list[ObservationSession]:
        """
        Return all stored observation sessions ordered newest first.
        """

        paths = sorted(
            self.config.session_path.glob("*.json"),
            reverse=True,
        )

        return [
            self._session_from_path(path)
            for path in paths
        ]

    def images_for_session(
            self,
            session: ObservationSession,
    ) -> list[CapturedImage]:
        """
        Return images associated with an observation session.
        """

        images = [
            image
            for image in self.images()
            if image.session_id == session.id
        ]

        return sorted(
            images,
            key=lambda image: image.captured_at,
        )

    def session(
            self,
            session_id: str,
    ) -> ObservationSession | None:
        """
        Return a stored observation session by session ID.
        """

        path = self.config.session_path / f"{session_id}.json"

        if not path.is_file():
            return None

        return self._session_from_path(path)

    @staticmethod
    def save_image_metadata(
            image: CapturedImage,
    ) -> Path:
        """
        Persist metadata for a captured image as JSON.

        Returns:
            Path of the created metadata file.
        """

        metadata_file = image.path.with_suffix(".json")

        data = {
            "captured_at": image.captured_at.isoformat(),
            "session_id": image.session_id,
        }

        with metadata_file.open(
                "w",
                encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
            )

        return metadata_file

    @staticmethod
    def _load_image_metadata(
            path: Path,
    ) -> dict:
        """
        Load metadata for an image from its JSON sidecar.
        """

        metadata_file = path.with_suffix(".json")

        if not metadata_file.is_file():
            return {}

        with metadata_file.open(
                "r",
                encoding="utf-8",
        ) as file:
            return json.load(file)

    def save_observation(
            self,
            observation: Observation,
    ) -> Path:
        """
        Persist an observation as JSON.

        Returns:
            Path of the created observation file.
        """

        output_file = (
                self.config.observation_path
                / f"{observation.id}.json"
        )

        data = {
            "id": observation.id,
            "detected_at": observation.detected_at.isoformat(),
            "image_filename": observation.image.filename,
            "detection_label": observation.detection_label,
            "detection_confidence": observation.detection_confidence,
            "objects": [
                {
                    "label": obj.label,
                    "confidence": obj.confidence,
                    "x1": obj.x1,
                    "y1": obj.y1,
                    "x2": obj.x2,
                    "y2": obj.y2,
                }
                for obj in observation.objects
            ],
            "classification_label": observation.classification_label,
            "classification_confidence": observation.classification_confidence,
        }

        with output_file.open(
                "w",
                encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
            )

        return output_file

    def _observation_from_path(
            self,
            path: Path,
    ) -> Observation:
        """
        Create an Observation from a persisted JSON file.
        """

        with path.open(
                "r",
                encoding="utf-8",
        ) as file:
            data = json.load(file)

        image_path = (
                self.config.image_path
                / data["image_filename"]
        )

        image = self.image_from_path(image_path)

        return Observation(
            image=image,
            detected_at=datetime.fromisoformat(
                data["detected_at"]
            ),
            detection_label=data["detection_label"],
            detection_confidence=data["detection_confidence"],
            objects=[
                DetectedObject(
                    label=obj["label"],
                    confidence=obj["confidence"],
                    x1=obj["x1"],
                    y1=obj["y1"],
                    x2=obj["x2"],
                    y2=obj["y2"],
                )
                for obj in data.get("objects", [])
            ],
            classification_label=data.get("classification_label"),
            classification_confidence=data.get("classification_confidence"),
        )

    def observations(self) -> list[Observation]:
        """
        Return all persisted observations.
        """

        observations = [
            self._observation_from_path(path)
            for path in self.config.observation_path.glob("*.json")
        ]

        return sorted(
            observations,
            key=lambda observation: observation.detected_at,
            reverse=True,
        )
