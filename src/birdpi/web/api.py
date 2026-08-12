"""
This module provides functionality to create and configure a Flask web application
with specified routes and templates.

It utilizes the `BirdPi` application and registers its associated routes through the
Flask blueprint mechanism. The module helps initialize the necessary components for
the web application, such as the static and template folder paths.

Functions:
    create_app(birdpi: BirdPi) -> Flask:
        Creates and configures a Flask application.
"""
from pathlib import Path

from flask import Flask

from birdpi.application import BirdPi
from birdpi.web.routes import register_routes


def create_app(birdpi: BirdPi) -> Flask:
    """
    Create Flask application.
    """

    package_root = Path(__file__).resolve().parent.parent

    app = Flask(
        __name__,
        template_folder=package_root / "templates",
        static_folder=package_root / "static",
    )

    web = register_routes(birdpi)
    app.register_blueprint(web)

    return app
