"""
Entry point for the BirdPi web server.
"""
from birdpi.application import BirdPi
from birdpi.bootstrap import initialize
from birdpi.web.api import create_app


def main() -> None:
    config = initialize()

    birdpi = BirdPi(config)

    app = create_app(birdpi)
    app.run(host="0.0.0.0", port=5000, )


if __name__ == "__main__":
    main()
