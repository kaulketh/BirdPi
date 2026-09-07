"""
Local command channel for the BirdPi runtime.
"""

import socket
from collections.abc import Callable
from pathlib import Path

from birdpi.exceptions import RuntimeCommandError
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


def run_command_server(
        socket_path: Path,
        command_handler: Callable[[str], str],
) -> None:
    """
    Run a simple local Unix socket command server.
    """

    if socket_path.exists():
        socket_path.unlink()

    server = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    server.bind(str(socket_path))
    server.listen()

    try:
        while True:
            connection, _ = server.accept()

            with connection:
                try:
                    command = (
                        connection.recv(1024)
                        .decode("utf-8")
                        .strip()
                    )

                    response = command_handler(
                        command
                    )

                    connection.sendall(
                        response.encode("utf-8")
                    )

                except OSError as error:
                    logger.warning(
                        "Runtime command connection failed: %s",
                        error,
                    )
    finally:
        server.close()

        if socket_path.exists():
            socket_path.unlink()


def send_command(
        socket_path: Path,
        command: str,
) -> str:
    """
    Send a command to the BirdPi runtime.
    """

    client = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    try:
        client.connect(
            str(socket_path)
        )

        client.sendall(
            command.encode("utf-8")
        )

        return (
            client.recv(1024)
            .decode("utf-8")
            .strip()
        )

    except OSError as error:
        raise RuntimeCommandError(
            f"Runtime command failed: {command}"
        ) from error

    finally:
        client.close()
