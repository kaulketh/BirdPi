"""
Handle the initialization and routing of the web interface for the BirdPi
application, including rendering templates, serving static files, and
defining endpoints for observation and session management.

This module provides the web interface integration for the BirdPi system by
defining routes, HTML rendering, and API endpoints for capturing images,
managing observations, viewing galleries, and accessing observation sessions.

Functions
---------
register_routes(birdpi: BirdPi) -> Blueprint
    Register the web interface routes for the BirdPi application, including
    rendering templates and defining routes for image gallery handling,
    observation control, and sessions management.
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
            "status_refresh_seconds": birdpi.config.web.refresh_interval_seconds,

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
        birdpi.capture()
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

    @web.route("/sessions")
    def sessions():
        observation_sessions = birdpi.storage.sessions()

        return render_template(
            "sessions.html",
            observation_sessions=observation_sessions,
        )

    @web.get("/sessions/<session_id>")
    def session_detail(session_id: str) -> str:
        session = birdpi.storage.session(session_id)

        if session is None:
            abort(404)

        images = birdpi.storage.images_for_session(session)

        return render_template(
            "session.html",
            session=session,
            images=images,
        )

    @web.route("/observations")
    def observations():
        """
        Show persisted observations.
        """

        observations = birdpi.storage.observations()

        return render_template(
            "observations.html",
            observations=observations,
        )

    return web
