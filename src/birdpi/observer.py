"""
Manage automatic BirdPi observations.

This module provides the `Observer` class, which is responsible for managing
automatic observations in the BirdPi system. It supports starting and stopping
observation sessions, and manages periodic image captures at a configured
interval. The `Observer` class uses threading to perform actions in the
background.

It interacts with the following components:
- `Config`: A configuration object that defines observation settings.
- `CapturedImage`: Represents a captured image.
- `ObservationSession`: Represents an observation session.
"""

import threading
import time
from collections.abc import Callable
from datetime import datetime, timedelta

from birdpi.config import Config
from birdpi.models import CapturedImage
from birdpi.models import ObservationSession
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class Observer:
    """
    Manage automatic BirdPi observations.
    """

    def __init__(
            self,
            config: Config,
            capture_callback: Callable[[str | None], CapturedImage],
    ) -> None:
        self.config = config
        self._capture_callback = capture_callback

        self._running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_capture_at: datetime | None = None
        self._next_capture_at: datetime | None = None
        self._state_lock = threading.Lock()
        self._session: ObservationSession | None = None

    def _run(self) -> None:
        """
        Run automatic observation loop.
        """

        logger.info(
            "Observation started with interval %s seconds",
            self.interval_seconds,
        )

        next_capture = time.monotonic() + self.interval_seconds

        self._next_capture_at = (
                datetime.now() + timedelta(seconds=self.interval_seconds))

        try:
            while not self._stop_event.is_set():
                wait_seconds = max(0, next_capture - time.monotonic(), )

                if self._stop_event.wait(wait_seconds):
                    break

                try:
                    image = self._capture_callback(
                        self._session.id
                        if self._session is not None
                        else None
                    )

                    self._last_capture_at = datetime.now()

                    if self._session is not None:
                        self._session.capture_count += 1

                    logger.info("Automatic image captured: %s", image.path, )

                except RuntimeError:
                    logger.exception(
                        "Automatic image capture failed"
                    )

                next_capture += self.interval_seconds
                while next_capture <= time.monotonic():
                    next_capture += self.interval_seconds

                wait_seconds = max(0, next_capture - time.monotonic(), )

                self._next_capture_at = (
                        datetime.now() + timedelta(seconds=wait_seconds))

        finally:
            with self._state_lock:
                if self._session is not None:
                    self._session.stopped_at = datetime.now()
                self._next_capture_at = None
                self._running = False
                self._thread = None

            logger.info("Observation stopped")

    @property
    def session(self) -> ObservationSession | None:
        """
        Return the current or most recent observation session.
        """

        return self._session

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

    @property
    def next_capture_at(self) -> datetime | None:
        """
        Return timestamp of the next scheduled automatic capture.
        """

        return self._next_capture_at

    def start(self) -> None:
        """
        Start automatic observation.
        """

        with self._state_lock:
            if self._running:
                logger.warning("Observation is already running")
                return

            self._stop_event.clear()
            self._session = ObservationSession(
                started_at=datetime.now(),
            )
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

        with self._state_lock:
            if not self._running:
                logger.warning("Observation is not running")
                return

            logger.info("Stopping observation")

            self._stop_event.set()
            thread = self._thread

        if thread is not None:
            thread.join()
