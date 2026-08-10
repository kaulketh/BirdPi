"""
This module provides web routes for accessing stored images, the latest captured
image, and triggering camera operations using the Flask framework.

The module is structured as a Flask `Blueprint` with several routes for
front-end integration and for interacting with a camera and storage system.
"""
from flask import Blueprint, redirect, render_template, send_from_directory, \
    url_for

from birdpi.camera.capture import Camera
from birdpi.storage import Storage

web = Blueprint("web", __name__)


def register_routes(
        storage: Storage,
        camera: Camera,
) -> Blueprint:
    @web.app_context_processor
    def inject_storage_status() -> dict:
        return {
            "image_count": storage.image_count(),
        }

    @web.get("/")
    def index() -> str:
        latest_image = storage.latest_image()

        return render_template(
            "index.html",
            latest_image=latest_image,
        )

    @web.get("/images/<path:filename>")
    def image(filename: str):
        return send_from_directory(
            storage.config.image_path,
            filename,
        )

    @web.post("/capture")
    def capture():
        camera.capture()
        return redirect(url_for("web.index"))

    return web
