"""
Control the BirdPi systemd service.
"""

import subprocess

from birdpi.exceptions import ServiceControlError


class BirdPiService:
    """
    Query and control the BirdPi systemd service.
    """

    SERVICE_NAME = "birdpi.service"

    def running(self) -> bool:
        try:
            result = subprocess.run(
                [
                    "systemctl",
                    "is-active",
                    "--quiet",
                    self.SERVICE_NAME,
                ],
                check=False,
            )

        except OSError as error:
            raise ServiceControlError(
                "Could not query BirdPi service state"
            ) from error

        return result.returncode == 0

    def start(self) -> None:
        self._control("start")

    def stop(self) -> None:
        self._control("stop")

    def restart(self) -> None:
        self._control("restart")

    def _control(
            self,
            action: str,
    ) -> None:
        try:
            subprocess.run(
                [
                    "sudo",
                    "systemctl",
                    action,
                    self.SERVICE_NAME,
                ],
                check=True,
            )

        except subprocess.CalledProcessError as error:
            raise ServiceControlError(
                f"Could not {action} "
                f"{self.SERVICE_NAME}: "
                f"exit code {error.returncode}"
            ) from error

        except OSError as error:
            raise ServiceControlError(
                f"Could not execute service action: {action}"
            ) from error
