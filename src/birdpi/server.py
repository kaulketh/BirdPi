"""
Entry point for running the BirdPi web application.

This module initializes the BirdPi web application using the `create_app`
function and runs the application on the specified host and port.
"""

from birdpi.config import load_config
from birdpi.storage import Storage
from birdpi.web.api import create_app


config = load_config()
storage = Storage(config)

app = create_app(storage)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)