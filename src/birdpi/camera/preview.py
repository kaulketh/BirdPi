"""
Low-resolution camera preview support for BirdPi.

The preview provides continuous grayscale frames for lightweight
motion detection without creating image files.
"""

import subprocess
from collections.abc import Iterator

import numpy as np

from birdpi.config import Config
from birdpi.exceptions import PreviewError


class CameraPreview:

    def __init__(
            self,
            config: Config,
            width: int = 640,
            height: int = 480,
            framerate: int = 5,
    ) -> None:
        self.config = config

        self.width = width
        self.height = height
        self.framerate = framerate

        self._process: subprocess.Popen | None = None

    @property
    def frame_size(self) -> int:
        """
        Return the size of one YUV420 frame in bytes.
        """

        return self.width * self.height * 3 // 2

    def start(self) -> None:
        """
        Start the camera preview process.
        """

        if self._process is not None:
            return

        command = [
            "rpicam-vid",

            "--width",
            str(self.width),

            "--height",
            str(self.height),

            "--framerate",
            str(self.framerate),

            "--codec",
            "yuv420",

            "--timeout",
            "0",

            "--nopreview",

            "-o",
            "-",
        ]

        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
        )

    def frames(self) -> Iterator[np.ndarray]:
        """
        Yield grayscale preview frames.
        """

        if self._process is None:
            raise PreviewError(
                "Camera preview is not running"
            )

        if self._process.stdout is None:
            raise PreviewError(
                "Camera preview output is unavailable"
            )

        while True:
            data = self._process.stdout.read(
                self.frame_size
            )

            if len(data) != self.frame_size:
                break

            # YUV420:
            # first width * height bytes are the luminance channel.
            y_plane = data[
                :self.width * self.height
            ]

            frame = np.frombuffer(
                y_plane,
                dtype=np.uint8,
            ).reshape(
                self.height,
                self.width,
            )

            yield frame

    def stop(self) -> None:
        """
        Stop the camera preview process.
        """

        if self._process is None:
            return

        self._process.terminate()

        try:
            self._process.wait(
                timeout=2,
            )

        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

        self._process = None

    def __enter__(self) -> "CameraPreview":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()
