"""
Runtime motion monitoring for BirdPi.

This module combines camera preview, daylight control,
motion detection, event creation and full-resolution capture.
"""

import time
from datetime import datetime

from birdpi.camera.capture import Camera
from birdpi.camera.preview import CameraPreview
from birdpi.daylight.controller import DayNightController
from birdpi.models import MotionEvent
from birdpi.motion.detector import MotionDetector
from birdpi.storage import Storage


class MotionMonitor:
    """
    Monitor preview frames and create motion events.
    """

    def __init__(
            self,
            preview: CameraPreview,
            detector: MotionDetector,
            camera: Camera,
            day_night: DayNightController,
            storage: Storage,
    ) -> None:
        self.preview = preview
        self.detector = detector
        self.camera = camera
        self.day_night = day_night
        self.storage = storage

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

                if not self.detector.detect(frame):
                    continue

                print(f"{index:06d} MOTION")

                event_started_at = datetime.now()

                event = MotionEvent(
                    id=event_started_at.strftime(
                        "%Y%m%d_%H%M%S_%f"
                    ),
                    started_at=event_started_at,
                )

                self.preview.stop()

                start = time.monotonic()

                image = self.camera.capture()

                elapsed = time.monotonic() - start

                event.add_image(image)
                event.close()
                event_path = self.storage.save_event(event)

                print(
                    f"Captured: {image.path} "
                    f"({elapsed:.3f} s)"
                )

                print(
                    f"Event: {event.id} "
                    f"Images: {len(event.images)} "
                    f"Active: {event.active}"
                )
                print(
                    f"Event saved: {event_path}"
                )

                self.detector.reset()
                self.preview.start()

        except KeyboardInterrupt:
            print("\nStopped")

        finally:
            self.preview.stop()
            self.day_night.close()