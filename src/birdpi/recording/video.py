"""
Record short videos using the Raspberry Pi camera.
"""
import subprocess
from pathlib import Path

from birdpi.config import Config
from birdpi.exceptions import VideoError


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

        except KeyboardInterrupt:
            if mp4_file.exists():
                mp4_file.unlink()

            raise

        except subprocess.CalledProcessError as error:
            if mp4_file.exists():
                mp4_file.unlink()

            command_name = (
                error.cmd[0]
                if isinstance(error.cmd, (list, tuple))
                   and error.cmd
                else "video command"
            )

            raise VideoError(
                f"{command_name} failed "
                f"with exit code {error.returncode}"
            ) from error

        except FileNotFoundError as error:
            if mp4_file.exists():
                mp4_file.unlink()

            raise VideoError(
                f"Required executable not found: {error.filename}"
            ) from error

        finally:
            if raw_file.exists():
                raw_file.unlink()

        return mp4_file
