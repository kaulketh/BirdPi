"""
Detector factory for BirdPi.
"""

from birdpi.config import Config
from birdpi.detection.detector import Detector
from birdpi.detection.dummy import DummyDetector
from birdpi.detection.motion import MotionDetector
from birdpi.detection.object import ObjectDetector


def create_detector(
        config: Config,
) -> Detector:
    """
    Create the configured primary detector.
    """

    match config.detector_type:
        case "dummy":
            return DummyDetector()

        case "motion":
            return MotionDetector(
                pixel_threshold=config.motion.pixel_threshold,
                motion_threshold=config.motion.threshold,
                block_threshold=config.motion.block_threshold,
                max_active_blocks=config.motion.max_active_blocks,
            )

        case _:
            raise ValueError(
                f"Unknown detector type: {config.detector_type}"
            )


def create_object_detector(
        config: Config,
) -> ObjectDetector:
    """
    Create the configured object detector.
    """

    return ObjectDetector(
        model_path=config.object_detection.model_path,
        confidence_threshold=(
            config.object_detection.confidence_threshold
        ),
        iou_threshold=config.object_detection.iou_threshold,
        input_size=config.object_detection.input_size,
    )
