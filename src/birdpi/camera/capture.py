"""
This module provides an interface for interacting with a Raspberry Pi Camera
to capture still images.

It contains a `Camera` class that enables capturing images and saving them to
a provided path. The module relies on external configuration and a subprocess
to invoke the camera functionality.
"""

import subprocess
import threading
from datetime import datetime
from pathlib import Path

from birdpi.config import Config
from birdpi.models import CapturedImage
from birdpi.storage import Storage


class Camera:
    """
    Raspberry Pi Camera interface.
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.storage: Storage = Storage(config)
        self._capture_lock = threading.Lock()

    def capture(
            self,
            filename: str | None = None,
            session_id: str | None = None,
    ) -> CapturedImage:
        with self._capture_lock:
            return self._capture(
                filename,
                session_id,
            )

    def _capture(
            self,
            filename: str | None = None,
            session_id: str | None = None,
    ) -> CapturedImage:
        """
        Captures an image using the camera and saves it to the storage location. The
        method ensures that required directories for storing images are available
        before performing the capture. The captured image metadata is also saved
        into the storage. If the capture process fails, a runtime error is raised.

        :param filename: Optional; Specifies the desired name of the captured image
            file. If not provided, a default name will be generated.
        :type filename: str or None
        :param session_id: Optional; Represents the identifier for the session
            associated with the captured image. Used for metadata purposes.
        :type session_id: str or None
        :return: The `CapturedImage` object representing the captured image with its
            associated metadata such as path, capture time, and session ID.
        :rtype: CapturedImage
        """
        self.storage.ensure_directories()
        output_file: Path = self.storage.next_image_path(filename)

        command = [
            "rpicam-still",

            "--width",
            str(self.config.camera.width),

            "--height",
            str(self.config.camera.height),

            "-o",
            str(output_file),

            "--nopreview"
        ]

        captured_at = datetime.now()

        try:
            subprocess.run(
                command,
                check=True,
            )

            image = CapturedImage(
                path=output_file,
                captured_at=captured_at,
                session_id=session_id,
            )

            self.storage.save_image_metadata(image)

        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                "Camera capture failed"
            ) from error

        return image

    @property
    def resolution(self) -> str:
        return (
            f"{self.config.camera.width} "
            f"× {self.config.camera.height}"
        )

    @property
    def model(self) -> str:
        """
        Return detected camera model.
        """

        result = subprocess.run(
            [
                "rpicam-hello",
                "--list-cameras",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines():
            line = line.strip()

            if line.startswith("0 :"):
                return line.split()[2]

        return "unknown"
