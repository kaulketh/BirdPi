"""
Runtime motion monitoring for BirdPi.

This module combines camera preview, daylight control,
motion detection, event creation, full-resolution capture,
and event video recording.
"""

import time
from collections.abc import Callable
from datetime import datetime

from birdpi.camera.capture import Camera
from birdpi.camera.preview import CameraPreview
from birdpi.daylight.controller import DayNightController
from birdpi.exceptions import VideoError
from birdpi.models import MotionEvent
from birdpi.motion.detector import MotionDetector
from birdpi.observation.state import ObservationState
from birdpi.recording.video import VideoRecorder
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class MotionMonitor:

    def __init__(
            self,
            preview: CameraPreview,
            detector: MotionDetector,
            camera: Camera,
            day_night: DayNightController,
            observation_state: ObservationState,
            storage: Storage,
            video_recorder: VideoRecorder,
            event_timeout_seconds: int,
            status_callback: Callable[[bool, str | None], None] | None = None,
            command_callback: Callable[[], None] | None = None,
    ) -> None:
        self.preview = preview
        self.detector = detector
        self.camera = camera
        self.day_night = day_night
        self.observation_state = observation_state
        self.storage = storage
        self.video_recorder = video_recorder

        self.event_timeout_seconds = event_timeout_seconds
        self._event: MotionEvent | None = None
        self._last_motion_at: float | None = None

        self.status_callback = status_callback
        self.command_callback = command_callback

        self._observation_active: bool | None = None

    def run(self) -> None:
        """
        Run motion monitoring until interrupted.
        """

        try:
            self.preview.start()

            for index, frame in enumerate(
                    self.preview.frames(),
                    start=1,
            ):
                self.day_night.update()

                if self.command_callback is not None:
                    self.command_callback()

                self._update_observation_state()

                if not self.observation_state.active:
                    continue

                now = time.monotonic()

                if self._event is not None:
                    if (
                            self._last_motion_at is not None
                            and now - self._last_motion_at
                            >= self.event_timeout_seconds
                    ):
                        self._close_event()

                if not self.detector.detect(frame):
                    continue

                logger.info(
                    "Motion detected at preview frame %06d",
                    index,
                )

                if self._event is None:
                    self._start_event()
                    self._capture_event_media()

                    # Start event timeout after photo/video recording.
                    self._last_motion_at = time.monotonic()

                else:
                    # Existing event: motion refreshes the timeout.
                    self._last_motion_at = time.monotonic()

                    logger.debug(
                        "Motion event active, timeout refreshed: %s",
                        self._event.id,
                    )

        except KeyboardInterrupt:
            logger.info(
                "Motion monitoring stopped"
            )

        finally:
            if self._event is not None:
                self._close_event()
            self.preview.stop()
            self.day_night.close()

    def _start_event(self) -> None:
        """
        Start a new motion event.
        """

        started_at = datetime.now()

        self._event = MotionEvent(
            id=started_at.strftime(
                "%Y%m%d_%H%M%S_%f"
            ),
            started_at=started_at,
        )

        if self.status_callback is not None:
            self.status_callback(
                True,
                self._event.id,
            )

        logger.info(
            "Motion event started: %s",
            self._event.id,
        )

    def _capture_event_media(self) -> None:
        """
        Capture one full-resolution image and one video
        for a newly started event.
        """

        if self._event is None:
            return

        self.preview.stop()

        try:
            start = time.monotonic()

            image = self.camera.capture()

            elapsed = time.monotonic() - start

            self._event.add_image(image)

            logger.info(
                "Image captured: %s (%.3f s)",
                image.path,
                elapsed,
            )

            video_path = self.storage.next_video_path(
                self._event.id
            )

            logger.info(
                "Recording event video: %s",
                video_path,
            )

            try:
                saved_video = self.video_recorder.record(
                    output_file=video_path,
                )

            except VideoError as error:
                logger.error(
                    "Event video recording failed: "
                    "event=%s error=%s",
                    self._event.id,
                    error,
                )

                self._event.video_filename = None

            else:
                self._event.video_filename = (
                    saved_video.name
                )

                logger.info(
                    "Event video saved: %s",
                    saved_video,
                )

        finally:
            self.detector.reset()
            self.preview.start()

    def _close_event(self) -> None:
        """
        Close and persist the active motion event.
        """

        if self._event is None:
            return

        self._event.close()

        event_path = self.storage.save_event(
            self._event
        )

        deleted_events = self.storage.cleanup_oldest_events()

        if deleted_events:
            logger.info(
                "Storage cleanup removed %d old event(s)",
                deleted_events,
            )

        if self.status_callback is not None:
            self.status_callback(
                False,
                self._event.id,
            )

        logger.info(
            "Motion event closed: %s, images=%d",
            self._event.id,
            len(self._event.images),
        )

        logger.info(
            "Motion event saved: %s",
            event_path,
        )

        self._event = None
        self._last_motion_at = None

    def _update_observation_state(self) -> None:
        """
        Handle changes between active observation and standby.
        """

        active = self.observation_state.active

        if active == self._observation_active:
            return

        self._observation_active = active

        if not active and self._event is not None:
            self._close_event()

        self.detector.reset()

        if active:
            logger.info(
                "Observation active: mode=%s, day_night=%s",
                self.observation_state.mode.value,
                self.observation_state.day_night.value,
            )
        else:
            logger.info(
                "Observation standby: mode=%s, day_night=%s",
                self.observation_state.mode.value,
                self.observation_state.day_night.value,
            )
