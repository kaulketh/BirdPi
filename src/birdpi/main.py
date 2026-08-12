"""
The entry point for running the BirdPi application.

This module initializes the application configuration, creates an instance
of the BirdPi application, and starts the application.

Functions:
    main(): Initializes BirdPi application and starts it.
"""

from birdpi.application import BirdPi
from birdpi.config import load_config
from birdpi.utils.logger import configure_logging


def main() -> None:
    configure_logging()
    config = load_config()
    app = BirdPi(config)
    app.run()


if __name__ == "__main__":
    main()
