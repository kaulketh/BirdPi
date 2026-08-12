"""
Entry point for initializing and running the BirdPi web application.

This module sets up the BirdPi system by loading the configuration, creating an
instance of BirdPi with the loaded configuration, and initializing the web
application with the BirdPi instance. Finally, it runs the web server on the
specified host and port.
"""
from birdpi.application import BirdPi
from birdpi.config import load_config
from birdpi.web.api import create_app

config = load_config()
birdpi = BirdPi(config)

app = create_app(birdpi)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, )
