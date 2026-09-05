"""
WSGI entry point for the BirdPi WebUI.
"""

from birdpi.bootstrap import initialize
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger
from birdpi.web.api import create_app

logger = get_logger(__name__)

config = initialize("web")

storage = Storage(config)
storage.ensure_directories()

app = create_app(
    config=config,
    storage=storage,
)

logger.info("BirdPi WebUI online")
