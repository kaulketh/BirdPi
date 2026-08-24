"""
Entry point for the BirdPi web server.
"""
from birdpi.bootstrap import initialize
from birdpi.web import create_app


def main() -> None:
    config = initialize()

    app = create_app(config)
    app.run()


if __name__ == "__main__":
    main()
