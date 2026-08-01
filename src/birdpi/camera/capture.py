"""
Interface for capturing still images using a Raspberry Pi Camera.

This module provides a `Camera` class designed for interaction with
the Raspberry Pi Camera. It allows configuration of the output directory
and capturing of still images using the `rpicam-still` command-line tool.
The captured images can be saved with a timestamp-based name or a user-provided name.
"""

import subprocess
from datetime import datetime
from pathlib import Path

from birdpi.config import CAMERA_WIDTH, CAMERA_HEIGHT


class Camera:
    """
    Raspberry Pi Camera interface.
    """

    def __init__(self, image_path: Path):
        self.image_path = Path(image_path)

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
            str(CAMERA_WIDTH),
            "--height",
            str(CAMERA_HEIGHT),
            "-o",
            str(output_file),
            "--nopreview"
        ]

        subprocess.run(
            command,
            check=True
        )

        return output_file
