"""
This module provides the Observer class, which manages the automatic observation
process for BirdPi, using camera captures at configured intervals.

Features include starting and stopping the observation loop, checking the running
status of the observation process, and retrieving the configured observation interval.
"""

import threading

from birdpi.camera.capture import Camera
from birdpi.config import Config


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

    def _run(self) -> None:
        """
        Run automatic observation loop.
        """

        while not self._stop_event.wait(
                self.interval_seconds
        ):
            self.camera.capture()

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

    def start(self) -> None:
        """
        Start automatic observation.
        """

        if self._running:
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._running = True
        self._thread.start()

    def stop(self) -> None:
        """
        Stop automatic observation.
        """

        if not self._running:
            return

        self._stop_event.set()

        if self._thread is not None:
            self._thread.join()

        self._running = False
        self._thread = None
