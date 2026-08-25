"""
Initialization module for loading configuration and setting up logging.
"""
from birdpi.config import load_config
from birdpi.utils.logger import configure_logging


def initialize():
    config = load_config()

    configure_logging(
        config.log_path
    )

    return config
