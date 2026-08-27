"""
A module to handle BirdPi storage, files, metadata, and directories.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

from birdpi.config import Config
from birdpi.models import CapturedImage
from birdpi.models import MotionEvent


class Storage:
    """
    Manage BirdPi file storage.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def disk_usage(self) -> dict:
        """
        Return disk usage information for the BirdPi data filesystem.
        """

        usage = shutil.disk_usage(
            self.config.data_path
        )

        total = usage.total
        used = usage.used
        free = usage.free

        free_percent = (
            free / total * 100
            if total
            else 0.0
        )

        return {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "total_gib": total / (1024 ** 3),
            "used_gib": used / (1024 ** 3),
            "free_gib": free / (1024 ** 3),
            "free_percent": free_percent,
        }

    def cleanup_oldest_events(self) -> int:
        """
        Delete oldest motion events until the configured
        target free space is reached.

        Return the number of deleted events.
        """

        usage = self.disk_usage()

        if (
                usage["free_percent"]
                > self.config.storage_min_free_percent
        ):
            return 0

        deleted = 0

        event_paths = sorted(
            self.config.event_path.glob("*.json")
        )

        for event_path in event_paths:
            if (
                    self.disk_usage()["free_percent"]
                    >= self.config.storage_target_free_percent
            ):
                break

            with event_path.open(
                    "r",
                    encoding="utf-8",
            ) as file:
                data = json.load(file)

            for filename in data.get("images", []):
                image_path = (
                        self.config.image_path
                        / filename
                )

                if image_path.is_file():
                    image_path.unlink()

                metadata_path = image_path.with_suffix(".json")

                if metadata_path.is_file():
                    metadata_path.unlink()

            video_filename = data.get("video_filename")

            if video_filename:
                video_path = (
                        self.config.video_path
                        / video_filename
                )

                if video_path.is_file():
                    video_path.unlink()

            event_path.unlink()

            deleted += 1

        return deleted

    def ensure_directories(self) -> None:
        """
        Create required directories if they do not exist.
        """

        self.config.image_path.mkdir(
            parents=True,
            exist_ok=True
        )
        self.config.event_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config.video_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config.runtime_status_path.parent.mkdir(
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

    def next_video_path(
            self,
            event_id: str,
    ) -> Path:
        return (
                self.config.video_path
                / f"event_{event_id}.mp4"
        )

    @staticmethod
    def image_from_path(
            path: Path,
    ) -> CapturedImage:
        """
        Create a CapturedImage from an image path.
        """

        metadata = Storage._load_image_metadata(path)

        if "captured_at" in metadata:
            captured_at = datetime.fromisoformat(
                metadata["captured_at"]
            )

        else:
            try:
                captured_at = datetime.strptime(
                    path.stem,
                    "image_%Y%m%d_%H%M%S",
                )

            except ValueError:
                captured_at = datetime.fromtimestamp(
                    path.stat().st_mtime
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

    @staticmethod
    def _delete_empty_event(
            event_path: Path,
            data: dict,
    ) -> bool:
        """
        Delete an event JSON if it no longer references any media.

        Return True if the event was deleted.
        """

        if (
                not data.get("images")
                and data.get("video_filename") is None
        ):
            event_path.unlink()
            return True

        return False

    def save_event(
            self,
            event: MotionEvent,
    ) -> Path:
        """
        Persist a motion event as JSON.
        """

        output_file = (
                self.config.event_path
                / f"{event.id}.json"
        )

        data = {
            "id": event.id,
            "started_at": event.started_at.isoformat(),
            "ended_at": (
                event.ended_at.isoformat()
                if event.ended_at is not None
                else None
            ),
            "images": [
                image.filename
                for image in event.images
            ],
            "video_filename": event.video_filename,
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

    def _event_from_path(
            self,
            path: Path,
    ) -> MotionEvent:
        """
        Create a MotionEvent from a persisted JSON file.
        """

        with path.open(
                "r",
                encoding="utf-8",
        ) as file:
            data = json.load(file)

        event = MotionEvent(
            id=data["id"],
            started_at=datetime.fromisoformat(
                data["started_at"]
            ),
            ended_at=(
                datetime.fromisoformat(data["ended_at"])
                if data["ended_at"]
                else None
            ),
            video_filename=data.get("video_filename"),
        )

        for filename in data.get("images", []):
            image = self.get_image(filename)

            if image is not None:
                event.add_image(image)

        return event

    def events(self) -> list[MotionEvent]:
        """
        Return all persisted motion events ordered newest first.
        """

        paths = sorted(
            self.config.event_path.glob("*.json"),
            reverse=True,
        )

        return [
            self._event_from_path(path)
            for path in paths
        ]

    def event(
            self,
            event_id: str,
    ) -> MotionEvent | None:
        """
        Return a persisted motion event by ID.
        """

        path = (
                self.config.event_path
                / f"{event_id}.json"
        )

        if not path.is_file():
            return None

        return self._event_from_path(path)

    def delete_image(
            self,
            filename: str,
    ) -> bool:
        """
        Delete an image and its JSON metadata sidecar.

        Return True if the image existed and was deleted.
        """

        image_path = (
                self.config.image_path
                / filename
        )

        if not image_path.is_file():
            return False

        metadata_path = image_path.with_suffix(".json")

        image_path.unlink()

        if metadata_path.is_file():
            metadata_path.unlink()

        for event_path in self.config.event_path.glob("*.json"):
            with event_path.open(
                    "r",
                    encoding="utf-8",
            ) as file:
                data = json.load(file)

            images = data.get("images", [])

            if filename not in images:
                continue

            data["images"] = [
                image_filename
                for image_filename in images
                if image_filename != filename
            ]
            if self._delete_empty_event(
                    event_path,
                    data,
            ):
                continue

            with event_path.open(
                    "w",
                    encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                )

        return True

    def clear_images(self) -> int:
        """
        Delete all stored images and their metadata sidecars.

        Return the number of deleted images.
        """

        deleted = 0

        for image_path in self.config.image_path.glob("*.jpg"):
            metadata_path = image_path.with_suffix(".json")

            image_path.unlink()

            if metadata_path.is_file():
                metadata_path.unlink()

            deleted += 1

        for event_path in self.config.event_path.glob("*.json"):
            with event_path.open(
                    "r",
                    encoding="utf-8",
            ) as file:
                data = json.load(file)

            if not data.get("images"):
                continue

            data["images"] = []

            if self._delete_empty_event(
                    event_path,
                    data,
            ):
                continue

            with event_path.open(
                    "w",
                    encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                )

        return deleted

    def delete_video(
            self,
            filename: str,
    ) -> bool:
        """
        Delete a video and remove its reference from persisted events.

        Return True if the video existed and was deleted.
        """

        video_path = (
                self.config.video_path
                / filename
        )

        if not video_path.is_file():
            return False

        video_path.unlink()

        for event_path in self.config.event_path.glob("*.json"):
            with event_path.open(
                    "r",
                    encoding="utf-8",
            ) as file:
                data = json.load(file)

            if data.get("video_filename") != filename:
                continue

            data["video_filename"] = None

            if self._delete_empty_event(
                    event_path,
                    data,
            ):
                continue

            with event_path.open(
                    "w",
                    encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                )

        return True

    def clear_videos(self) -> int:
        """
        Delete all stored videos and remove their event references.

        Return the number of deleted videos.
        """

        deleted = 0

        for video_path in self.config.video_path.glob("*.mp4"):
            video_path.unlink()
            deleted += 1

        for event_path in self.config.event_path.glob("*.json"):
            with event_path.open(
                    "r",
                    encoding="utf-8",
            ) as file:
                data = json.load(file)

            if data.get("video_filename") is None:
                continue

            data["video_filename"] = None

            if self._delete_empty_event(
                    event_path,
                    data,
            ):
                continue

            with event_path.open(
                    "w",
                    encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                )

        return deleted
