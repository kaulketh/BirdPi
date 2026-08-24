"""
The main application module of the BirdPi system.

This module initializes and connects the core BirdPi components used for
continuous motion monitoring and event-based image capture.
"""

from birdpi.camera.capture import Camera
from birdpi.camera.preview import CameraPreview
from birdpi.config import Config
from birdpi.daylight.controller import DayNightController
from birdpi.daylight.sun import Daylight
from birdpi.lighting.ir_lights import IRLights
from birdpi.models import CapturedImage
from birdpi.motion.detector import MotionDetector
from birdpi.motion.monitor import MotionMonitor
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class BirdPi:
    """
    Main application class for the BirdPi system.
    """

    def __init__(
            self,
            config: Config,
    ) -> None:
        self.config = config

        self.storage = Storage(config)
        self.storage.ensure_directories()

        self.camera = Camera(config)
        self.preview = CameraPreview(config)

        self.motion_detector = MotionDetector()

        self.daylight = Daylight(config)

        self.ir_lights = IRLights(
            left_pin=config.ir.left_pin,
            right_pin=config.ir.right_pin,
        )

        self.day_night = DayNightController(
            daylight=self.daylight,
            ir_lights=self.ir_lights,
            motion_detector=self.motion_detector,
            check_interval_seconds=(
                config.daylight.check_interval_seconds
            ),
        )

        self.motion_monitor = MotionMonitor(
            preview=self.preview,
            detector=self.motion_detector,
            camera=self.camera,
            day_night=self.day_night,
        )

    def run(self) -> None:
        """
        Start BirdPi motion monitoring.
        """

        logger.info("BirdPi online")

        try:
            self.motion_monitor.run()

        finally:
            self.ir_lights.close()

            logger.info("BirdPi offline")

    def capture(
            self,
            filename: str | None = None,
    ) -> CapturedImage:
        """
        Capture a full-resolution image manually.
        """

        image = self.camera.capture(
            filename=filename,
        )

        logger.info(
            "Image captured: %s",
            image.path,
        )

        return image
