"""
Main entry point for BirdPi.
"""

import signal

from birdpi.application import BirdPi
from birdpi.bootstrap import initialize


def _handle_sigterm(
        signum,
        frame,
) -> None:
    raise KeyboardInterrupt


def main() -> None:
    signal.signal(
        signal.SIGTERM,
        _handle_sigterm,
    )

    config = initialize("runtime")

    birdpi = BirdPi(config)
    birdpi.run()


if __name__ == "__main__":
    main()
