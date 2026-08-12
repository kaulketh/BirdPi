"""
Manage BirdPi file storage.

This module handles operations related to managing the BirdPi file storage,
including creating required directories, handling image file paths, counting
stored images, and retrieving images or their adjacent neighbors.

Classes:
    Storage: Offers methods for managing file storage operations such as directory
             management and image retrieval.

"""
from datetime import datetime
from pathlib import Path

from birdpi.config import Config
from birdpi.models import CapturedImage


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

        return sum(
            1
            for _ in self.config.image_path.glob("*.jpg")
        )

    def images(self) -> list[CapturedImage]:
        """
        Return all stored images ordered from newest to oldest.
        """

        paths = sorted(
            self.config.image_path.glob("*.jpg"),
            reverse=True,
        )

        return [
            self.image_from_path(path)
            for path in paths
        ]

    @staticmethod
    def image_from_path(path: Path) -> CapturedImage:
        """
        Create a CapturedImage from an image path.
        """

        captured_at = datetime.strptime(
            path.stem,
            "image_%Y%m%d_%H%M%S",
        )

        return CapturedImage(
            path=path,
            captured_at=captured_at,
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
