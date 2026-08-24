"""
BirdPi configuration module.

This module contains the configuration management for BirdPi, including
default configuration creation and associated functionality.
"""

from dataclasses import dataclass
from pathlib import Path

from birdpi.utils.geo import LOCATIONS


@dataclass(frozen=True, slots=True)
class DaylightConfig:
    check_interval_seconds: int


@dataclass(frozen=True, slots=True)
class LocationConfig:
    latitude: float
    longitude: float


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


@dataclass(frozen=True, slots=True)
class MotionConfig:
    pixel_threshold: int
    min_area: float
    reference_interval: int
    event_timeout_seconds: int


@dataclass(frozen=True, slots=True)
class WebConfig:
    refresh_interval_seconds: int


@dataclass(slots=True)
class Config:
    """
    BirdPi configuration.
    """
    location_name: str

    data_path: Path
    image_path: Path
    session_path: Path
    observation_path: Path
    observation_interval_seconds: int
    event_path: Path
    detector_type: str
    classifier_type: str

    motion: MotionConfig
    camera: CameraConfig
    ir: IRLightConfig
    web: WebConfig
    object_detection: ObjectDetectionConfig

    location: LocationConfig

    daylight: DaylightConfig


def load_config() -> Config:
    """
    Create the default BirdPi configuration.
    """

    location_name = "HOME"
    data_path = Path("/home/kaulketh/birdpi-data")
    image_path = data_path / "images"
    session_path = data_path / "sessions"
    observation_path = data_path / "observations"
    event_path = data_path / "events"

    return Config(
        location_name=location_name,
        data_path=data_path,
        image_path=image_path,
        session_path=session_path,
        observation_path=observation_path,
        event_path=event_path,

        camera=CameraConfig(width=4608, height=2592),
        ir=IRLightConfig(enabled=True, left_pin=20, right_pin=21, ),

        observation_interval_seconds=300,

        web=WebConfig(refresh_interval_seconds=30, ),

        detector_type="motion",
        classifier_type="dummy",

        motion=MotionConfig(
            pixel_threshold=60,
            min_area=1000,
            reference_interval=5,
            event_timeout_seconds=8,
        ),
        object_detection=ObjectDetectionConfig(
            model_path=Path(
                "/home/kaulketh/birdpi/models/yolo11n.onnx"
            ),
            confidence_threshold=0.25,
            iou_threshold=0.45,
            input_size=640,
        ),
        location=LocationConfig(
            latitude=LOCATIONS[location_name].latitude,
            longitude=LOCATIONS[location_name].longitude
        ),
        daylight=DaylightConfig(
            check_interval_seconds=60,
        ),
    )
