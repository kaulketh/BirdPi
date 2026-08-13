"""
This module provides the Observer class, which manages the automatic observation
process for BirdPi, using camera captures at configured intervals.

Features include starting and stopping the observation loop, checking the running
status of the observation process, and retrieving the configured observation interval.
"""

import threading
from datetime import datetime

from birdpi.camera.capture import Camera
from birdpi.config import Config
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class Observer:
    """
    Manage automatic BirdPi observations.
    """

    def __init__(
            self,
            config: Config,
            camera: Camera,
    ) -> None:
        self.config = config
        self.camera = camera
        self._running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_capture_at: datetime | None = None

    def _run(self) -> None:
        """
        Run automatic observation loop.
        """

        logger.info(
            "Observation started with interval %s seconds",
            self.interval_seconds,
        )

        try:
            while not self._stop_event.wait(
                    self.interval_seconds
            ):
                try:
                    image = self.camera.capture()
                    self._last_capture_at = datetime.now()
                    logger.info("Automatic image captured: %s", image, )

                except Exception:
                    logger.exception(
                        "Automatic image capture failed"
                    )

        finally:
            self._running = False
            logger.info("Observation stopped")

    @property
    def running(self) -> bool:
        """
        Return whether automatic observation is running.
        """

        return self._running

    @property
    def interval_seconds(self) -> int:
        """
        Return the configured observation interval in seconds.
        """

        return self.config.observation_interval_seconds

    @property
    def last_capture_at(self) -> datetime | None:
        """
        Return timestamp of the last successful automatic capture.
        """

        return self._last_capture_at

    def start(self) -> None:
        """
        Start automatic observation.
        """

        if self._running:
            logger.warning("Observation is already running")
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="birdpi-observer",
        )

        self._running = True
        self._thread.start()

    def stop(self) -> None:
        """
        Stop automatic observation.
        """

        if not self._running:
            logger.warning("Observation is not running")
            return

        logger.info("Stopping observation")

        self._stop_event.set()

        if self._thread is not None:
            self._thread.join()

        self._thread = None
