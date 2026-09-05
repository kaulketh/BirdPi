"""
BirdPi configuration module.

This module contains the configuration management for BirdPi, including
default configuration creation and associated functionality.
"""

from dataclasses import dataclass
from pathlib import Path

from birdpi.utils.geo import LOCATIONS


@dataclass(frozen=True, slots=True)
class CameraConfig:
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class DaylightConfig:
    check_interval_seconds: int


@dataclass(frozen=True, slots=True)
class IRLightConfig:
    enabled: bool
    left_pin: int
    right_pin: int


@dataclass(frozen=True, slots=True)
class LocationConfig:
    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class MotionConfig:
    pixel_threshold: int
    min_area: float
    reference_interval: int
    event_timeout_seconds: int


@dataclass(frozen=True, slots=True)
class ObjectDetectionConfig:
    model_path: Path
    confidence_threshold: float
    iou_threshold: float
    input_size: int


@dataclass(frozen=True, slots=True)
class TelegramConfig:
    enabled: bool
    token_env: str
    chat_id_env: str


@dataclass(frozen=True, slots=True)
class VideoConfig:
    width: int
    height: int
    framerate: int
    duration_seconds: int


@dataclass(frozen=True, slots=True)
class WebConfig:
    refresh_interval_seconds: int


@dataclass(slots=True)
class Config:
    location_name: str

    data_path: Path
    image_path: Path
    event_path: Path
    video_path: Path
    log_path: Path
    runtime_status_path: Path

    detector_type: str
    classifier_type: str

    camera: CameraConfig
    video: VideoConfig
    ir: IRLightConfig
    motion: MotionConfig
    web: WebConfig
    object_detection: ObjectDetectionConfig
    location: LocationConfig
    daylight: DaylightConfig

    storage_min_free_percent: float
    storage_target_free_percent: float

    telegram: TelegramConfig

    runtime_command_socket_path: Path

    manual_video_max_duration_seconds: int


def load_config() -> Config:
    location_name = "HOME"
    data_path = Path("/home/kaulketh/birdpi-data")
    image_path = data_path / "images"
    event_path = data_path / "events"
    video_path = data_path / "videos"
    log_path = data_path / "logs" / "birdpi.log"
    runtime_status_path = (
            data_path
            / "status"
            / "runtime.json"
    )
    runtime_command_socket_path = (
            data_path
            / "status"
            / "birdpi.sock"
    )

    return Config(
        location_name=location_name,
        data_path=data_path,
        image_path=image_path,
        event_path=event_path,
        video_path=video_path,
        log_path=log_path,
        runtime_status_path=runtime_status_path,
        runtime_command_socket_path=runtime_command_socket_path,

        camera=CameraConfig(
            width=4608, height=2592),
        video=VideoConfig(
            width=1920, height=1080,
            framerate=30, duration_seconds=15,
        ),
        ir=IRLightConfig(enabled=True, left_pin=20, right_pin=21, ),

        web=WebConfig(refresh_interval_seconds=30, ),

        detector_type="motion",
        classifier_type="dummy",

        motion=MotionConfig(
            pixel_threshold=30,  # 60,
            min_area=3000,
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

        storage_min_free_percent=20.0,
        storage_target_free_percent=30.0,

        telegram=TelegramConfig(
            enabled=True,
            token_env="BIRDPI_TELEGRAM_TOKEN",
            chat_id_env="BIRDPI_TELEGRAM_CHAT_ID",
        ),
        manual_video_max_duration_seconds=60,
    )
