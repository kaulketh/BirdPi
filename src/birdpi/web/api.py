"""
Create and configure the BirdPi Flask web application.
"""

from pathlib import Path

from flask import Flask

from birdpi.config import Config
from birdpi.storage import Storage
from birdpi.web.routes import register_routes


def create_app(
        config: Config,
        storage: Storage,
) -> Flask:
    """
    Create Flask application.
    """

    package_root = Path(__file__).resolve().parent.parent

    app = Flask(
        __name__,
        template_folder=package_root / "templates",
        static_folder=package_root / "static",
    )

    web = register_routes(
        config=config,
        storage=storage,
    )

    app.register_blueprint(web)

    return app
