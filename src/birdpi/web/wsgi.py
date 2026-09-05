"""
WSGI entry point for the BirdPi WebUI.
"""

from birdpi.bootstrap import initialize
from birdpi.storage import Storage
from birdpi.web.api import create_app

config = initialize()

storage = Storage(config)
storage.ensure_directories()

app = create_app(
    config=config,
    storage=storage,
)
