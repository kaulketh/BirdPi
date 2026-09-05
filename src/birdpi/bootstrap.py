"""
Initialization module for loading configuration and setting up logging.
"""

from typing import Literal

from birdpi.config import load_config
from birdpi.utils.logger import configure_logging

Component = Literal[
    "runtime",
    "web",
    "bot",
]


def initialize(
        component: Component = "runtime",
):
    config = load_config()

    log_files = {
        "runtime": config.log_path,
        "web": config.web_log_path,
        "bot": config.bot_log_path,
    }

    configure_logging(
        log_files[component]
    )

    return config
