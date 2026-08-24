"""
Runtime motion monitoring for BirdPi.

This module combines camera preview, daylight control,
motion detection, and full-resolution capture.
"""

import time

from birdpi.camera.capture import Camera
from birdpi.camera.preview import CameraPreview
from birdpi.daylight.controller import DayNightController
from birdpi.motion.detector import MotionDetector


class MotionMonitor:
    """
    Monitor preview frames and capture full-resolution images on motion.
    """

    def __init__(
            self,
            preview: CameraPreview,
            detector: MotionDetector,
            camera: Camera,
            day_night: DayNightController,
    ) -> None:
        self.preview = preview
        self.detector = detector
        self.camera = camera
        self.day_night = day_night

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

                self.preview.stop()

                start = time.monotonic()

                image = self.camera.capture()

                elapsed = time.monotonic() - start

                print(
                    f"Captured: {image.path} "
                    f"({elapsed:.3f} s)"
                )

                self.detector.reset()
                self.preview.start()

        except KeyboardInterrupt:
            print("\nStopped")

        finally:
            self.preview.stop()
            self.day_night.close()
