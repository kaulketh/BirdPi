"""
Runtime status handling for BirdPi.

The runtime service writes the current system state to a JSON file.
The web interface can read this file without accessing hardware directly.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class RuntimeStatus:
    """
    Represent the current BirdPi runtime state.
    """

    mode: str = "unknown"
    ir_mode: str = "off"
    motion_active: bool = False
    current_event_id: str | None = None
    last_event_id: str | None = None
    last_update: str | None = None
    camera_model: str | None = None
    camera_resolution: str | None = None


class RuntimeStatusStore:
    """
    Persist and load BirdPi runtime status.
    """

    def __init__(
            self,
            path: Path,
    ) -> None:
        self.path = path

    def write(
            self,
            status: RuntimeStatus,
    ) -> None:
        """
        Persist the current runtime status.
        """

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        status.last_update = (
            datetime.now()
            .astimezone()
            .isoformat()
        )

        with self.path.open(
                "w",
                encoding="utf-8",
        ) as file:
            json.dump(
                asdict(status),
                file,
                indent=4,
            )

    def read(self) -> RuntimeStatus:
        """
        Load the current runtime status.

        Return defaults if no status file exists.
        """

        if not self.path.is_file():
            return RuntimeStatus()

        with self.path.open(
                "r",
                encoding="utf-8",
        ) as file:
            data = json.load(file)

        return RuntimeStatus(
            mode=data.get("mode", "unknown"),
            ir_mode=data.get("ir_mode", "off"),
            motion_active=data.get(
                "motion_active",
                False,
            ),
            current_event_id=data.get(
                "current_event_id"
            ),
            last_event_id=data.get(
                "last_event_id"
            ),
            last_update=data.get(
                "last_update"
            ),
            camera_model=data.get("camera_model"),
            camera_resolution=data.get("camera_resolution"),
        )
