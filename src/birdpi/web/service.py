import subprocess


class BirdPiService:
    """
    Query and control the BirdPi systemd service.
    """

    SERVICE_NAME = "birdpi.service"

    def running(self) -> bool:
        result = subprocess.run(
            [
                "systemctl",
                "is-active",
                "--quiet",
                self.SERVICE_NAME,
            ]
        )

        return result.returncode == 0

    def start(self) -> None:
        subprocess.run(
            [
                "sudo",
                "systemctl",
                "start",
                self.SERVICE_NAME,
            ],
            check=True,
        )

    def stop(self) -> None:
        subprocess.run(
            [
                "sudo",
                "systemctl",
                "stop",
                self.SERVICE_NAME,
            ],
            check=True,
        )

    def restart(self) -> None:
        subprocess.run(
            [
                "sudo",
                "systemctl",
                "restart",
                self.SERVICE_NAME,
            ],
            check=True,
        )
