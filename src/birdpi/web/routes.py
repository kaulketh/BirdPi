"""
A module for registering and managing web routes for a Flask application.

This module defines and sets up the routes required for the application
to handle HTTP requests. The primary purpose of this module is to configure
the web endpoints required to respond to client requests.

"""
from flask import Flask


def register_routes(app: Flask) -> None:
    """
    Register all web routes.
    """

    @app.get("/")
    def index() -> str:
        return "BirdPi is running"
