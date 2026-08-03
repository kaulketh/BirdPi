"""
A module for creating and configuring a Flask web application.

This module is used to initialize and return a Flask application instance
with predefined routes registered to it. The `create_app` function is the
primary entry point for application setup and configuration.
"""
from flask import Flask

from birdpi.web.routes import register_routes


def create_app() -> Flask:
    """
    Create Flask application.
    """

    app = Flask(__name__)
    register_routes(app)
    return app
