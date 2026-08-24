"""
Object detector factory for BirdPi.
"""

from birdpi.config import Config
from birdpi.detection.object import ObjectDetector


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