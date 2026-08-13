"""
Provides routes and request handling logic for the Flask-based web interface of the BirdPi application.

This module defines and registers routes within a Flask Blueprint to expose web functionalities such
as capturing images, viewing galleries, and retrieving system-related data. The routes interact with
the BirdPi application instance to serve data and handle user actions through the web interface.

Functions:
    - register_routes: Registers all routes and context processors for the web Blueprint.
"""
import socket

from flask import abort, Blueprint, redirect, render_template, \
    send_from_directory, \
    url_for

from birdpi.application import BirdPi
from birdpi.system import format_uptime, get_uptime, get_cpu_temperature

web = Blueprint("web", __name__)


def register_routes(birdpi: BirdPi) -> Blueprint:
    storage = birdpi.storage
    camera = birdpi.camera

    @web.app_context_processor
    def inject_status() -> dict:
        return {
            "image_count": storage.image_count(),
            "hostname": socket.gethostname(),
            "uptime": format_uptime(get_uptime()),
            "cpu_temperature": get_cpu_temperature(),
            "camera_resolution": camera.resolution,
            "camera_model": camera.model,
            "observer_running": birdpi.observer.running,
            "observation_interval": birdpi.observer.interval_seconds,
            "last_capture_at": birdpi.observer.last_capture_at,
            "next_capture_at": birdpi.observer.next_capture_at,
            "status_refresh_seconds": birdpi.config.status_refresh_seconds,
            "web_refresh_interval": birdpi.config.web_refresh_interval_seconds,
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

    @web.get("/gallery")
    def gallery() -> str:
        images = storage.images()

        return render_template(
            "gallery.html",
            images=images,
        )

    @web.get("/gallery/<path:filename>")
    def gallery_image(filename: str) -> str:
        image = storage.get_image(filename)

        if image is None:
            abort(404)

        newer, older = storage.adjacent_images(image)

        return render_template(
            "image.html",
            image=image,
            newer=newer,
            older=older,
        )

    @web.post("/observation/start")
    def observation_start():
        birdpi.observer.start()

        return redirect(url_for("web.index"))

    @web.post("/observation/stop")
    def observation_stop():
        birdpi.observer.stop()

        return redirect(url_for("web.index"))

    return web
