"""
This module provides an interface for interacting with a Raspberry Pi Camera
to capture still images.

It contains a `Camera` class that enables capturing images and saving them to
a provided path. The module relies on external configuration and a subprocess
to invoke the camera functionality.
"""

import subprocess
import threading
from pathlib import Path

from birdpi.config import Config
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
    ) -> Path:
        """
        Capture a still image.

        Returns:
            Path of created image.
        """

        with self._capture_lock:
            return self._capture(filename)

    def _capture(self, filename: str | None = None) -> Path:
        """
        Capture an image using the configured camera settings and save it to the specified
        location or to the next available filename in the storage if no filename is
        explicitly provided. Ensures that the necessary directories for storage are created
        before capturing the image.

        :param filename: Optional custom filename for the captured image. If None, a new
                         unique filename is generated automatically by the storage configuration.
                         The storage determines the file extension and name formatting.
        :type filename: str | None

        :return: The path to the saved image file.
        :rtype: Path
        """
        self.storage.ensure_directories()
        output_file: Path = self.storage.next_image_path(filename)

        command = [
            "rpicam-still",

            "--width",
            str(self.config.camera_width),

            "--height",
            str(self.config.camera_height),

            "-o",
            str(output_file),

            "--nopreview"
        ]

        try:
            subprocess.run(
                command,
                check=True
            )

        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                "Camera capture failed"
            ) from error

        return output_file

    @property
    def resolution(self) -> str:
        return (
            f"{self.config.camera_width} "
            f"× {self.config.camera_height}"
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
