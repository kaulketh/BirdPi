"""
Blueprint for the web interface, providing routes for camera image handling
and system status integration.

This module defines a Flask Blueprint that sets up web interface routes
for interacting with the camera, retrieving stored images, and presenting
system information such as uptime and hostname. The `register_routes`
function binds the provided `Storage` and `Camera` instances to the
created routes.

Functions:
    register_routes(storage: Storage, camera: Camera) -> Blueprint:
        Registers routes for the web interface and configures the necessary
        context for rendering templates with storage and system status.

"""
import socket

from flask import Blueprint, redirect, render_template, send_from_directory, \
    url_for

from birdpi.camera.capture import Camera
from birdpi.storage import Storage
from birdpi.system import format_uptime, get_uptime, get_cpu_temperature

web = Blueprint("web", __name__)


def register_routes(
        storage: Storage,
        camera: Camera,
) -> Blueprint:
    @web.app_context_processor
    def inject_storage_status() -> dict:
        return {
            "image_count": storage.image_count(),
            "hostname": socket.gethostname(),
            "uptime": format_uptime(get_uptime()),
            "cpu_temperature": get_cpu_temperature(),
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
