"""
Handle the BirdPi web interface routes.
"""

import socket

from flask import (
    abort,
    Blueprint,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

from birdpi.application import BirdPi
from birdpi.system import (
    format_uptime,
    get_cpu_temperature,
    get_uptime,
)

web = Blueprint("web", __name__)


def register_routes(
        birdpi: BirdPi,
) -> Blueprint:
    """
    Register BirdPi web interface routes.
    """

    storage = birdpi.storage
    camera = birdpi.camera

    @web.app_context_processor
    def inject_status() -> dict:
        events = storage.events()
        latest_event = events[0] if events else None
        return {
            "image_count": storage.image_count(),
            "hostname": socket.gethostname(),
            "uptime": format_uptime(
                get_uptime()
            ),
            "cpu_temperature": get_cpu_temperature(),
            "camera_resolution": camera.resolution,
            "camera_model": camera.model,

            "night_mode": birdpi.day_night.night_mode,
            "ir_mode": birdpi.ir_lights.mode.value,

            "event_count": len(events),
            "latest_event": latest_event,

            "status_refresh_seconds": (
                birdpi.config.web.refresh_interval_seconds
            ),
        }

    @web.get("/")
    def index() -> str:
        latest_image = storage.latest_image()

        return render_template(
            "index.html",
            latest_image=latest_image,
        )

    @web.get("/images/<path:filename>")
    def image(
            filename: str,
    ):
        return send_from_directory(
            storage.config.image_path,
            filename,
        )

    @web.get("/videos/<path:filename>")
    def video(
            filename: str,
    ):
        return send_from_directory(
            storage.config.video_path,
            filename,
        )

    @web.post("/capture")
    def capture():
        birdpi.capture()

        return redirect(
            url_for("web.index")
        )

    @web.get("/gallery")
    def gallery() -> str:
        images = storage.images()

        return render_template(
            "gallery.html",
            images=images,
        )

    @web.get("/gallery/<path:filename>")
    def gallery_image(
            filename: str,
    ) -> str:
        image = storage.get_image(
            filename
        )

        if image is None:
            abort(404)

        newer, older = storage.adjacent_images(
            image
        )

        return render_template(
            "image.html",
            image=image,
            newer=newer,
            older=older,
        )

    @web.get("/events")
    def events() -> str:
        motion_events = storage.events()

        return render_template(
            "events.html",
            events=motion_events,
        )

    @web.get("/events/<event_id>")
    def event_detail(
            event_id: str,
    ) -> str:
        event = storage.event(
            event_id
        )

        if event is None:
            abort(404)

        return render_template(
            "event.html",
            event=event,
        )

    return web
