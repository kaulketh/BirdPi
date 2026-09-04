"""
Runtime command client for the BirdPi WebUI.
"""

from birdpi.config import Config
from birdpi.runtime.command import send_command


class RuntimeCommandClient:
    """
    Send commands to the running BirdPi runtime service.
    """

    def __init__(
            self,
            config: Config,
    ) -> None:
        self.socket_path = (
            config.runtime_command_socket_path
        )

    def send(
            self,
            command: str,
    ) -> str:
        return send_command(
            self.socket_path,
            command,
        )

    def capture_image(self) -> str:
        return self.send(
            "capture_image"
        )

    def video_start(self) -> str:
        return self.send(
            "video_start"
        )

    def video_stop(self) -> str:
        return self.send(
            "video_stop"
        )

    def ir_off(self) -> str:
        return self.send(
            "ir_off"
        )

    def ir_left(self) -> str:
        return self.send(
            "ir_left"
        )

    def ir_right(self) -> str:
        return self.send(
            "ir_right"
        )

    def ir_both(self) -> str:
        return self.send(
            "ir_both"
        )
