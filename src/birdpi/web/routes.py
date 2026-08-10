"""
A module for registering and managing web routes for a Flask application.

This module defines and sets up the routes required for the application
to handle HTTP requests. The primary purpose of this module is to configure
the web endpoints required to respond to client requests.

"""
from flask import Flask, render_template, send_from_directory

from birdpi.camera.capture import Camera
from birdpi.storage import Storage


def register_routes(
    app: Flask,
    storage: Storage,
    camera: Camera,
) -> None:
    """
    Register all web routes.
    """

    @app.get("/")
    def index() -> str:
        latest_image = storage.latest_image()

        return render_template(
            "index.html",
            latest_image=latest_image,
        )

    @app.get("/images/<path:filename>")
    def image(filename: str):
        return send_from_directory(
            storage.config.image_path,
            filename,
        )