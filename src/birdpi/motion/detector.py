"""
Motion detection for BirdPi preview frames.
"""

import cv2
import numpy as np


class MotionDetector:
    def __init__(
            self,
            pixel_threshold: int = 20,
            min_area: float = 1000,
            reference_interval: int = 5,
    ) -> None:
        self.pixel_threshold = pixel_threshold
        self.min_area = min_area
        self.reference_interval = reference_interval

        self._reference_frame: np.ndarray | None = None
        self._frame_count = 0

    def detect(
            self,
            frame: np.ndarray,
    ) -> bool:

        blurred = cv2.GaussianBlur(
            frame,
            (21, 21),
            0,
        )

        if self._reference_frame is None:
            self._reference_frame = blurred
            return False

        difference = cv2.absdiff(
            self._reference_frame,
            blurred,
        )

        threshold = cv2.threshold(
            difference,
            self.pixel_threshold,
            255,
            cv2.THRESH_BINARY,
        )[1]

        threshold = cv2.dilate(
            threshold,
            None,
            iterations=2,
        )

        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        areas = [
            cv2.contourArea(contour)
            for contour in contours
        ]

        max_area = max(areas, default=0)

        print(
            f"contours={len(contours):3d} "
            f"max_area={max_area:8.1f}"
        )

        self._frame_count += 1

        if self._frame_count >= self.reference_interval:
            self._reference_frame = blurred
            self._frame_count = 0

        return max_area >= self.min_area

    def reset(self) -> None:
        self._reference_frame = None
        self._frame_count = 0
