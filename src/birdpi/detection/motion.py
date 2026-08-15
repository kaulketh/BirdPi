"""
Motion detection support for BirdPi.

This module provides the MotionDetector class, which compares captured
images to detect relevant changes between consecutive frames.
"""

from datetime import datetime

import numpy as np
from PIL import Image

from birdpi.detection.detector import Detector
from birdpi.models import CapturedImage, Observation
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class MotionDetector(Detector):
    """
    Detect motion between consecutive captured images.
    """

    def __init__(
            self,
            pixel_threshold: int = 25,
            motion_threshold: float = 0.02,
            block_threshold: float = 0.05,
            max_active_blocks: int = 12,
    ) -> None:
        self._previous_image: CapturedImage | None = None
        self.pixel_threshold = pixel_threshold
        self.motion_threshold = motion_threshold
        self.block_threshold = block_threshold
        self.max_active_blocks = max_active_blocks

    def detect(
            self,
            image: CapturedImage,
    ) -> list[Observation]:
        """
        Detect motion between the current and previous image.
        """

        if self._previous_image is None:
            self._previous_image = image
            return []

        previous = self._load_image(self._previous_image)
        current = self._load_image(image)

        difference = np.abs(current - previous)

        changed_pixels = difference > self.pixel_threshold

        block_height = 40
        block_width = 40

        block_scores = []

        for y in range(0, changed_pixels.shape[0], block_height):
            for x in range(0, changed_pixels.shape[1], block_width):
                block = changed_pixels[
                    y:y + block_height,
                    x:x + block_width
                ]

                block_scores.append(
                    float(np.mean(block))
                )

        active_blocks = sum(
            score >= self.block_threshold
            for score in block_scores
        )

        motion_score = float(
            np.mean(changed_pixels)
        )

        self._previous_image = image

        logger.info(
            "Motion score: %.4f, active blocks: %d/%d",
            motion_score,
            active_blocks,
            len(block_scores),
        )

        if motion_score < self.motion_threshold:
            return []

        if active_blocks > self.max_active_blocks:
            logger.info(
                "Motion rejected as global scene change: %d active blocks",
                active_blocks,
            )
            return []

        return [
            Observation(
                image=image,
                detected_at=datetime.now(),
                detection_label="motion",
                detection_confidence=motion_score,
            )
        ]

    @staticmethod
    def _load_image(image: CapturedImage) -> np.ndarray:
        with Image.open(image.path) as source:
            source = source.convert("L")
            source = source.resize((320, 240))

            return np.asarray(
                source,
                dtype=np.int16,
            )
