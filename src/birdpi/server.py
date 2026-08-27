"""
Entry point for the BirdPi web server.
"""

from birdpi.bootstrap import initialize
from birdpi.storage import Storage
from birdpi.web.api import create_app


def main() -> None:
    config = initialize()

    storage = Storage(config)
    storage.ensure_directories()

    app = create_app(
        config=config,
        storage=storage,
    )

    app.run(
        host="0.0.0.0",
        port=5000,
    )


if __name__ == "__main__":
    main()
