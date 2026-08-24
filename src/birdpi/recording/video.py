import subprocess
from pathlib import Path

from birdpi.config import Config


class VideoRecorder:
    """
    Record short videos using the Raspberry Pi camera.
    """

    def __init__(
            self,
            config: Config,
    ) -> None:
        self.config = config

    def record(
            self,
            output_file: Path,
            duration_seconds: int | None = None,
    ) -> Path:
        """
        Record a video.

        Incomplete output files are removed if recording fails
        or is interrupted.
        """

        duration = (
            duration_seconds
            if duration_seconds is not None
            else self.config.video.duration_seconds
        )

        timeout_ms = duration * 1000

        command = [
            "rpicam-vid",
            "--width",
            str(self.config.video.width),
            "--height",
            str(self.config.video.height),
            "--framerate",
            str(self.config.video.framerate),
            "--timeout",
            str(timeout_ms),
            "--codec",
            "h264",
            "--nopreview",
            "-o",
            str(output_file),
        ]

        try:
            subprocess.run(
                command,
                check=True,
            )

        except (subprocess.CalledProcessError, KeyboardInterrupt):
            if output_file.exists():
                output_file.unlink()

            raise

        return output_file
