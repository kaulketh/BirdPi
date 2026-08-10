"""
This module provides the creation and configuration of a Flask application.

It initializes a Flask application instance, sets the template and static
folder paths based on the package root directory, and registers application
routes.
"""
from pathlib import Path

from flask import Flask

from birdpi.camera.capture import Camera
from birdpi.storage import Storage
from birdpi.web.routes import register_routes


def create_app(
    storage: Storage,
    camera: Camera,
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

    register_routes(app, storage, camera)

    return app
