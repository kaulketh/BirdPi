"""
Runtime motion monitoring for BirdPi.

This module combines camera preview, daylight control,
motion detection, event creation, full-resolution capture
and event video recording.
"""

import time
from datetime import datetime

from birdpi.camera.capture import Camera
from birdpi.camera.preview import CameraPreview
from birdpi.daylight.controller import DayNightController
from birdpi.models import MotionEvent
from birdpi.motion.detector import MotionDetector
from birdpi.recording.video import VideoRecorder
from birdpi.storage import Storage


class MotionMonitor:
    """
    Monitor preview frames and group motion captures into events.
    """

    def __init__(
            self,
            preview: CameraPreview,
            detector: MotionDetector,
            camera: Camera,
            day_night: DayNightController,
            storage: Storage,
            video_recorder: VideoRecorder,
            event_timeout_seconds: int,
    ) -> None:
        self.preview = preview
        self.detector = detector
        self.camera = camera
        self.day_night = day_night
        self.storage = storage
        self.video_recorder = video_recorder
        self.event_timeout_seconds = event_timeout_seconds

        self._event: MotionEvent | None = None
        self._last_motion_at: float | None = None

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

                print(f"{index:06d} MOTION")

                self._last_motion_at = now

                new_event = self._event is None

                if new_event:
                    self._start_event()

                self._capture_event_media(
                    record_video=new_event
                )

        except KeyboardInterrupt:
            print("\nStopped")

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

        print(
            f"Event started: {self._event.id}"
        )

    def _capture_event_media(
            self,
            record_video: bool,
    ) -> None:
        """
        Capture a full-resolution image and optionally
        record one video for a newly started event.
        """

        if self._event is None:
            return

        self.preview.stop()

        try:
            start = time.monotonic()

            image = self.camera.capture()

            elapsed = time.monotonic() - start

            self._event.add_image(image)

            print(
                f"Captured: {image.path} "
                f"({elapsed:.3f} s)"
            )

            print(
                f"Event images: "
                f"{len(self._event.images)}"
            )

            if record_video:
                video_path = self.storage.next_video_path(
                    self._event.id
                )

                print(
                    f"Recording video: {video_path}"
                )

                self.video_recorder.record(
                    output_file=video_path,
                )

                self._event.video_filename = (
                    video_path.name
                )

                print(
                    f"Video saved: {video_path}"
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

        print(
            f"Event closed: {self._event.id} "
            f"Images: {len(self._event.images)}"
        )

        print(
            f"Event saved: {event_path}"
        )

        self._event = None
        self._last_motion_at = None
