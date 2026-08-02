"""
This module provides an interface for interacting with a Raspberry Pi Camera
to capture still images.

It contains a `Camera` class that enables capturing images and saving them to
a provided path. The module relies on external configuration and a subprocess
to invoke the camera functionality.
"""

import subprocess
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

    def capture(self, filename: str | None = None) -> Path:
        """
        Capture a still image.

        Returns:
            Path of created image.
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
