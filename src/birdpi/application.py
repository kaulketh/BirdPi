"""
The main application module of the BirdPi system.

This module initializes and connects the core BirdPi components used for
continuous motion monitoring and event-based image capture.
"""

import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Queue

from birdpi.camera.capture import Camera
from birdpi.camera.preview import CameraPreview
from birdpi.config import Config
from birdpi.daylight.controller import DayNightController
from birdpi.daylight.sun import Daylight
from birdpi.lighting.ir_lights import IRLights
from birdpi.lighting.ir_lights import IRMode
from birdpi.models import CapturedImage
from birdpi.motion.detector import MotionDetector
from birdpi.motion.monitor import MotionMonitor
from birdpi.recording.video import VideoRecorder
from birdpi.runtime.command import run_command_server
from birdpi.runtime.status import RuntimeStatus, RuntimeStatusStore
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class BirdPi:

    def __init__(
            self,
            config: Config,
    ) -> None:
        self.config = config

        self.storage = Storage(config)
        self.storage.ensure_directories()

        self.runtime_status = RuntimeStatusStore(config.runtime_status_path)
        self.status = RuntimeStatus()

        self.camera = Camera(config)
        self.status.camera_model = self.camera.model
        self.status.camera_resolution = str(
            self.camera.resolution
        )

        self.runtime_status.write(
            self.status
        )
        self.preview = CameraPreview(config)

        self.video_recorder = VideoRecorder(config)

        self.motion_detector = MotionDetector(
            pixel_threshold=config.motion.pixel_threshold,
            min_area=config.motion.min_area,
            reference_interval=config.motion.reference_interval,
        )

        self.daylight = Daylight(config)

        self.ir_lights = IRLights(
            left_pin=config.ir.left_pin,
            right_pin=config.ir.right_pin,
        )

        self.day_night = DayNightController(
            daylight=self.daylight,
            ir_lights=self.ir_lights,
            motion_detector=self.motion_detector,
            check_interval_seconds=(
                config.daylight.check_interval_seconds
            ),
            status_callback=self._update_day_night_status,
        )

        self.motion_monitor = MotionMonitor(
            preview=self.preview,
            detector=self.motion_detector,
            camera=self.camera,
            day_night=self.day_night,
            storage=self.storage,
            video_recorder=self.video_recorder,
            event_timeout_seconds=(
                config.motion.event_timeout_seconds
            ),
            status_callback=self._update_motion_status,
            command_callback=self._process_commands,
        )
        self.command_thread = threading.Thread(
            target=run_command_server,
            args=(
                config.runtime_command_socket_path,
                self._handle_command,
            ),
            daemon=True,
        )
        self.command_queue: Queue[str] = Queue()

        self.manual_video_process = None
        self.manual_video_path: Path | None = None
        self.manual_video_started_at: float | None = None
        self.manual_video_stop_event = threading.Event()
        self.manual_video_started_event = threading.Event()
        self.manual_video_finished_event = threading.Event()

    def run(self) -> None:
        """
        Start BirdPi motion monitoring.
        """

        logger.info("BirdPi online")
        self.command_thread.start()

        try:
            self.motion_monitor.run()

        finally:
            self.ir_lights.close()
            logger.info("BirdPi offline")

    def capture(
            self,
            filename: str | None = None,
    ) -> CapturedImage:
        """
        Capture a full-resolution image manually.
        """
        self.day_night.update(force=True)

        image = self.camera.capture(
            filename=filename,
        )

        logger.info(
            "Image captured: %s",
            image.path,
        )

        return image

    def _update_day_night_status(
            self,
            night_mode: bool,
            ir_mode: IRMode,
    ) -> None:
        self.status.mode = ("night" if night_mode else "day")
        self.status.ir_mode = ir_mode.value
        self.runtime_status.write(self.status)

    def _update_motion_status(
            self,
            motion_active: bool,
            event_id: str | None,
    ) -> None:
        self.status.motion_active = motion_active

        if motion_active:
            self.status.current_event_id = event_id
        else:
            self.status.current_event_id = None
            self.status.last_event_id = event_id

        self.runtime_status.write(
            self.status
        )

    def _handle_command(
            self,
            command: str,
    ) -> str:

        match command:

            case "video_start":
                if self.manual_video_process is not None:
                    return "VIDEO ALREADY RUNNING"
                self.command_queue.put("video_start")
                if not self.manual_video_started_event.wait(timeout=5):
                    return "VIDEO START TIMEOUT"
                return "VIDEO STARTED"

            case "video_stop":
                if self.manual_video_process is None:
                    return "VIDEO NOT RUNNING"
                self.manual_video_stop_event.set()
                if not self.manual_video_finished_event.wait(timeout=10):
                    return "VIDEO STOP TIMEOUT"
                return "VIDEO STOPPED"

            case "capture_image":
                self.command_queue.put("capture_image")
                return "CAPTURE QUEUED"

            case "ir_off":
                self.ir_lights.off()
                self.status.ir_mode = self.ir_lights.mode.value
                self.runtime_status.write(self.status)
                return "IR OFF"

            case "ir_left":
                self.ir_lights.left_on()
                self.status.ir_mode = self.ir_lights.mode.value
                self.runtime_status.write(self.status)
                return "IR LEFT"

            case "ir_right":
                self.ir_lights.right_on()
                self.status.ir_mode = self.ir_lights.mode.value
                self.runtime_status.write(self.status)
                return "IR RIGHT"

            case "ir_both":
                self.ir_lights.on()
                self.status.ir_mode = self.ir_lights.mode.value
                self.runtime_status.write(self.status)
                return "IR BOTH"

            case _:
                return "unknown command"

    def _process_commands(self) -> None:
        while not self.command_queue.empty():
            command = self.command_queue.get()

            match command:
                case "capture_image":
                    logger.info("Processing manual image capture")
                    self.preview.stop()
                    try:
                        self.capture()
                    finally:
                        self.preview.start()

                case "video_start":
                    logger.info("Processing manual video start")
                    self._start_manual_video()

                case "video_stop":
                    logger.info("Processing manual video stop")
                    self._stop_manual_video()

                case _:
                    logger.warning("Unknown queued command: %s", command, )

    def _start_manual_video(self) -> None:
        if self.manual_video_process is not None:
            logger.info("Manual video already running")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        raw_path = (
                self.config.video_path
                / f"manual_{timestamp}.h264"
        )

        self.manual_video_path = raw_path.with_suffix(".mp4")
        self.manual_video_started_at = time.monotonic()

        self.manual_video_stop_event.clear()
        self.manual_video_started_event.clear()
        self.manual_video_finished_event.clear()

        self.preview.stop()

        command = [
            "rpicam-vid",
            "--width",
            str(self.config.video.width),
            "--height",
            str(self.config.video.height),
            "--framerate",
            str(self.config.video.framerate),
            "--codec",
            "h264",
            "--timeout",
            "0",
            "--nopreview",
            "-o",
            str(raw_path),
        ]

        self.manual_video_process = subprocess.Popen(command)
        self.status.manual_video_active = True
        self.runtime_status.write(self.status)
        self.manual_video_started_event.set()

        logger.info("Manual video started: %s", self.manual_video_path, )

        try:
            stopped_manually = self.manual_video_stop_event.wait(
                timeout=self.config.manual_video_max_duration_seconds
            )

            if stopped_manually:
                logger.info("Manual video stop requested")
            else:
                logger.info("Manual video reached maximum duration")

        finally:
            self._stop_manual_video()

    def _stop_manual_video(self) -> None:
        if self.manual_video_process is None:
            return

        process = self.manual_video_process
        self.manual_video_process = None

        process.terminate()
        process.wait()

        raw_path = self.manual_video_path.with_suffix(".h264")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(self.config.video.framerate),
                "-i",
                str(raw_path),
                "-c",
                "copy",
                str(self.manual_video_path),
            ],
            check=True,
        )

        if raw_path.exists():
            raw_path.unlink()

        logger.info("Manual video saved: %s", self.manual_video_path, )
        self.manual_video_started_at = None
        self.preview.start()
        self.status.manual_video_active = False
        self.runtime_status.write(self.status)
        self.manual_video_finished_event.set()
