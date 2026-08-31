"""
Record short videos using the Raspberry Pi camera.
"""
import subprocess
from pathlib import Path

from birdpi.config import Config


class VideoRecorder:

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
        Record a video and store it as MP4.
        """

        duration = (
            duration_seconds
            if duration_seconds is not None
            else self.config.video.duration_seconds
        )

        timeout_ms = (duration * 1000) + 1000

        raw_file = output_file.with_suffix(".h264")
        mp4_file = output_file.with_suffix(".mp4")

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
            str(raw_file),
        ]

        try:
            subprocess.run(
                command,
                check=True,
            )

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-framerate",
                    str(self.config.video.framerate),
                    "-i",
                    str(raw_file),
                    "-c",
                    "copy",
                    str(mp4_file),
                ],
                check=True,
            )

        except (
                subprocess.CalledProcessError,
                KeyboardInterrupt,
        ):
            if raw_file.exists():
                raw_file.unlink()

            if mp4_file.exists():
                mp4_file.unlink()

            raise

        finally:
            if raw_file.exists():
                raw_file.unlink()

        return mp4_file
