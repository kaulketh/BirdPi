"""
Detector factory for BirdPi.
"""

from birdpi.config import Config
from birdpi.detection.detector import Detector
from birdpi.detection.dummy import DummyDetector
from birdpi.detection.motion import MotionDetector


def create_detector(config: Config) -> Detector:
    """
    Create the configured detector implementation.
    """

    match config.detector_type:
        case "dummy":
            return DummyDetector()

        case "motion":
            return MotionDetector(
                pixel_threshold=config.motion_pixel_threshold,
                motion_threshold=config.motion_threshold,
                block_threshold=config.motion_block_threshold,
                max_active_blocks=config.motion_max_active_blocks,
            )

        case _:
            raise ValueError(
                f"Unknown detector type: {config.detector_type}"
            )