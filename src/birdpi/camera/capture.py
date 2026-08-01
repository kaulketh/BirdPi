"""
Module providing an interface for capturing images using the Raspberry Pi Camera.

This module defines the `Camera` class which facilitates the capturing of still
images via the Raspberry Pi Camera system. The captured images are stored in
the specified directory with the option to name the file or use a timestamp-based
default naming convention.
"""

import subprocess
from datetime import datetime
from pathlib import Path


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
            "-o",
            str(output_file),
            "--nopreview"
        ]

        subprocess.run(
            command,
            check=True
        )

        return output_file
