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
from birdpi.lighting.ir_lights import IRMode
from birdpi.models import CapturedImage
from birdpi.motion.detector import MotionDetector
from birdpi.motion.monitor import MotionMonitor
from birdpi.recording.video import VideoRecorder
from birdpi.runtime.status import RuntimeStatus, RuntimeStatusStore
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class BirdPi:

    def __init__(
            self,
            config: Config,
    ) -> None:
        self.config = config

        self.storage = Storage(config)
        self.storage.ensure_directories()

        self.runtime_status = RuntimeStatusStore(config.runtime_status_path)
        self.status = RuntimeStatus()

        self.camera = Camera(config)
        self.status.camera_model = self.camera.model
        self.status.camera_resolution = str(
            self.camera.resolution
        )

        self.runtime_status.write(
            self.status
        )
        self.preview = CameraPreview(config)

        self.video_recorder = VideoRecorder(config)

        self.motion_detector = MotionDetector(
            pixel_threshold=config.motion.pixel_threshold,
            min_area=config.motion.min_area,
            reference_interval=config.motion.reference_interval,
        )

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
            status_callback=self._update_day_night_status,
        )

        self.motion_monitor = MotionMonitor(
            preview=self.preview,
            detector=self.motion_detector,
            camera=self.camera,
            day_night=self.day_night,
            storage=self.storage,
            video_recorder=self.video_recorder,
            event_timeout_seconds=(
                config.motion.event_timeout_seconds
            ),
            status_callback=self._update_motion_status,
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
        self.day_night.update(force=True)

        image = self.camera.capture(
            filename=filename,
        )

        logger.info(
            "Image captured: %s",
            image.path,
        )

        return image

    def _update_day_night_status(
            self,
            night_mode: bool,
            ir_mode: IRMode,
    ) -> None:
        self.status.mode = ("night" if night_mode else "day")
        self.status.ir_mode = ir_mode.value
        self.runtime_status.write(self.status)

    def _update_motion_status(
            self,
            motion_active: bool,
            event_id: str | None,
    ) -> None:
        self.status.motion_active = motion_active

        if motion_active:
            self.status.current_event_id = event_id
        else:
            self.status.current_event_id = None
            self.status.last_event_id = event_id

        self.runtime_status.write(
            self.status
        )
