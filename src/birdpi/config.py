"""
BirdPi configuration module.

This module contains the configuration management for BirdPi, including
default configuration creation and associated functionality.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CameraConfig:
    width: int
    height: int


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

    motion: MotionConfig
    camera: CameraConfig
    web: WebConfig

    @property
    def status_refresh_seconds(self) -> int:
        return min(self.observation_interval_seconds, 30)


def load_config() -> Config:
    """
    Create the default BirdPi configuration.
    """

    data_path = Path("/home/kaulketh/birdpi-data")
    image_path = data_path / "images"
    session_path = data_path / "sessions"
    observation_path = data_path / "observations"

    observer_interval = 10

    detector_type = "motion"

    return Config(
        data_path=data_path,
        image_path=image_path,
        session_path=session_path,
        observation_path=observation_path,

        camera=CameraConfig(
            width=3280,
            height=2464, ),

        observation_interval_seconds=observer_interval,

        web=WebConfig(
            refresh_interval_seconds=10,
        ),

        detector_type=detector_type,

        motion=MotionConfig(
            pixel_threshold=25,
            threshold=0.02,
            block_threshold=0.05,
            max_active_blocks=12,
        ),
    )
