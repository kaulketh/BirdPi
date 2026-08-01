"""
Module for interfacing with a Raspberry Pi Camera.

This module provides a Camera class to capture still images using a Raspberry
Pi Camera. The captured images are saved to a specified path using the
configuration provided during the initialization of the Camera instance.
"""

import subprocess
from datetime import datetime
from pathlib import Path


class Camera:
    """
    Raspberry Pi Camera interface.
    """

    def __init__(self, config):
        self.config = config
        self.image_path = config.image_path

    def capture(self, filename: str | None = None) -> Path:
        """
        Capture a still image.

        Returns:
            Path of created image.
        """

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.jpg"

        output_file = self.image_path / filename

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

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
