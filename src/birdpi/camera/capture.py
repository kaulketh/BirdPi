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
from time import sleep

from birdpi.camera.ir_lights import IRLights, IRMode
from birdpi.config import Config
from birdpi.models import CapturedImage
from birdpi.storage import Storage


class Camera:
    """
    Represents a camera capable of capturing images with optional infrared mode functionality.

    Provides mechanisms to capture images, store them, and manage infrared light settings,
    if applicable, based on configurations.

    :ivar config: Configuration object containing settings for the camera including
        resolution, infrared settings, and other properties.
    :type config: Config
    :ivar storage: Storage handler to manage directories and file paths for storing
        captured images and their metadata.
    :type storage: Storage
    :ivar ir_lights: Object for managing infrared lighting, if enabled in the configuration.
        None if infrared lights are disabled.
    :type ir_lights: IRLights | None
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.storage: Storage = Storage(config)
        self._capture_lock = threading.Lock()

        self.ir_lights: IRLights | None = None

        if self.config.camera.ir.enabled:
            self.ir_lights = IRLights(
                left_pin=self.config.camera.ir.left_pin,
                right_pin=self.config.camera.ir.right_pin,
            )

    def capture(
            self,
            filename: str | None = None,
            session_id: str | None = None,
            ir_mode: IRMode = IRMode.OFF,
    ) -> CapturedImage:
        with self._capture_lock:
            return self._capture(
                filename,
                session_id,
                ir_mode,
            )

    def _capture(
            self,
            filename: str | None = None,
            session_id: str | None = None,
            ir_mode: IRMode = IRMode.OFF,
    ) -> CapturedImage:
        """
        Captures an image using the camera, saving it to the specified filename or a dynamically
        generated path. This method also allows configuring the infrared (IR) lights during
        capturing. The captured image is returned as an instance of CapturedImage.

        :param filename: The desired filename for the captured image. If None, a new filename
            will be generated automatically.
        :type filename: str | None

        :param session_id: An optional unique identifier for the session in which the image
            was captured. If None, the session ID will not be stored in the metadata.
        :type session_id: str | None

        :param ir_mode: The mode of the infrared (IR) lights during the capture. Defaults to
            IRMode.OFF. If the IR lights are enabled, the method waits briefly for them to
            activate before capturing the image.
        :type ir_mode: IRMode

        :return: An instance of CapturedImage representing the captured image, including its
            path, capture timestamp, and metadata like session ID if provided.
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

        if self.ir_lights is not None:
            self.ir_lights.set_mode(ir_mode)

            if ir_mode is not IRMode.OFF:
                sleep(0.5)

        captured_at = datetime.now()

        try:
            try:
                subprocess.run(
                    command,
                    check=True,
                )

            except subprocess.CalledProcessError as error:
                raise RuntimeError(
                    "Camera capture failed"
                ) from error

            image = CapturedImage(
                path=output_file,
                captured_at=captured_at,
                session_id=session_id,
            )

            self.storage.save_image_metadata(image)

            return image

        finally:
            if self.ir_lights is not None:
                self.ir_lights.set_mode(IRMode.OFF)

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
