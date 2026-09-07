"""
Video recording for BirdPi.
"""

import signal
import subprocess
from pathlib import Path

from birdpi.config import Config
from birdpi.exceptions import VideoError


class VideoRecorder:
    """
    Record BirdPi event videos using rpicam-vid.
    """

    STOP_TIMEOUT_SECONDS = 5

    def __init__(
            self,
            config: Config,
    ) -> None:
        self.config = config

    def record(
            self,
            output_file: Path,
    ) -> Path:
        """
        Record an event video and convert it to MP4.
        """

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
            "0",
            "--codec",
            "h264",
            "--nopreview",
            "-o",
            str(raw_file),
        ]

        process: subprocess.Popen | None = None

        try:
            try:
                process = subprocess.Popen(
                    command
                )

            except FileNotFoundError as error:
                raise VideoError(
                    "Required executable not found: "
                    "rpicam-vid"
                ) from error

            # rpicam-vid runs continuously. Waiting for the
            # configured duration should therefore time out.
            try:
                return_code = process.wait(
                    timeout=self.config.video.duration_seconds
                )

            except subprocess.TimeoutExpired:
                # Expected case: configured recording duration reached.
                process.send_signal(
                    signal.SIGINT
                )

                try:
                    return_code = process.wait(
                        timeout=self.STOP_TIMEOUT_SECONDS
                    )

                except subprocess.TimeoutExpired as error:
                    process.kill()
                    process.wait()

                    raise VideoError(
                        "rpicam-vid did not stop "
                        "after SIGINT"
                    ) from error

            else:
                # rpicam-vid terminated before the requested
                # recording duration.
                raise VideoError(
                    "rpicam-vid stopped unexpectedly "
                    f"with exit code {return_code}"
                )

            acceptable_return_codes = {
                0,
                -signal.SIGINT,
                128 + signal.SIGINT,
            }

            if return_code not in acceptable_return_codes:
                raise VideoError(
                    "rpicam-vid failed while stopping "
                    f"with exit code {return_code}"
                )

            if (
                    not raw_file.is_file()
                    or raw_file.stat().st_size == 0
            ):
                raise VideoError(
                    "rpicam-vid produced no video data"
                )

            try:
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

            except FileNotFoundError as error:
                raise VideoError(
                    "Required executable not found: ffmpeg"
                ) from error

            except subprocess.CalledProcessError as error:
                raise VideoError(
                    "ffmpeg failed "
                    f"with exit code {error.returncode}"
                ) from error

            return mp4_file

        except KeyboardInterrupt:
            if (
                    process is not None
                    and process.poll() is None
            ):
                process.send_signal(
                    signal.SIGINT
                )

                try:
                    process.wait(
                        timeout=self.STOP_TIMEOUT_SECONDS
                    )

                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

            if mp4_file.exists():
                mp4_file.unlink()

            raise

        except VideoError:
            if mp4_file.exists():
                mp4_file.unlink()

            raise

        finally:
            if raw_file.exists():
                raw_file.unlink()
