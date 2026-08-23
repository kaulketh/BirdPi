"""
BirdPi configuration module.

This module contains the configuration management for BirdPi, including
default configuration creation and associated functionality.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class IRLightConfig:
    enabled: bool
    left_pin: int
    right_pin: int


@dataclass(frozen=True, slots=True)
class ObjectDetectionConfig:
    model_path: Path
    confidence_threshold: float
    iou_threshold: float
    input_size: int


@dataclass(frozen=True, slots=True)
class CameraConfig:
    width: int
    height: int
    ir: IRLightConfig


@dataclass(frozen=True, slots=True)
class MotionConfig:
    pixel_threshold: int
    threshold: float
    block_threshold: float
    max_active_blocks: int


@dataclass(frozen=True, slots=True)
class WebConfig:
    refresh_interval_seconds: int


@dataclass(slots=True)
class Config:
    """
    BirdPi configuration.
    """

    data_path: Path
    image_path: Path
    session_path: Path
    observation_path: Path
    observation_interval_seconds: int
    detector_type: str
    classifier_type: str

    motion: MotionConfig
    camera: CameraConfig
    web: WebConfig
    object_detection: ObjectDetectionConfig


def load_config() -> Config:
    """
    Create the default BirdPi configuration.
    """

    data_path = Path("/home/kaulketh/birdpi-data")
    image_path = data_path / "images"
    session_path = data_path / "sessions"
    observation_path = data_path / "observations"

    return Config(
        data_path=data_path,
        image_path=image_path,
        session_path=session_path,
        observation_path=observation_path,

        camera=CameraConfig(
            width=4608,
            height=2592,
            ir=IRLightConfig(
                enabled=True,
                left_pin=20,
                right_pin=21,
            ),
        ),

        observation_interval_seconds=300,

        web=WebConfig(
            refresh_interval_seconds=30,
        ),

        detector_type="motion",
        classifier_type="dummy",

        motion=MotionConfig(
            pixel_threshold=25,
            threshold=0.01,  # 0.02
            block_threshold=0.05,
            max_active_blocks=20,  # 12
        ),
        object_detection=ObjectDetectionConfig(
            model_path=Path(
                "/home/kaulketh/birdpi/models/yolo11n.onnx"
            ),
            confidence_threshold=0.25,
            iou_threshold=0.45,
            input_size=640,
        ),
    )
