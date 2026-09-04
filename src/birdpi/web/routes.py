"""
Handle the BirdPi web interface routes.
"""

import socket
from datetime import datetime

from flask import (
    abort,
    Blueprint,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)

from birdpi.config import Config
from birdpi.runtime.status import RuntimeStatusStore
from birdpi.storage import Storage
from birdpi.system import (
    format_uptime,
    get_cpu_temperature,
    get_uptime,
)
from birdpi.web.runtime import RuntimeCommandClient
from birdpi.web.service import BirdPiService

web = Blueprint("web", __name__)


def register_routes(
        config: Config,
        storage: Storage,
) -> Blueprint:
    """
    Register BirdPi web interface routes.
    """
    service = BirdPiService()
    runtime_status = RuntimeStatusStore(
        config.runtime_status_path
    )

    runtime = RuntimeCommandClient(
        config
    )

    @web.app_context_processor
    def inject_status() -> dict:
        events = storage.events()
        latest_event = events[0] if events else None
        status = runtime_status.read()
        runtime_last_update = (
            datetime.fromisoformat(status.last_update)
            if status.last_update
            else None
        )

        disk = storage.disk_usage()
        storage_used_percent = (100.0 - disk["free_percent"])

        if storage_used_percent >= 80:
            storage_level = "critical"
        elif storage_used_percent >= 70:
            storage_level = "warning"
        else:
            storage_level = "normal"

        return {

            "hostname": socket.gethostname(),
            "uptime": format_uptime(
                get_uptime()
            ),
            "cpu_temperature": get_cpu_temperature(),

            "storage_total_gib": disk["total_gib"],
            "storage_used_gib": disk["used_gib"],
            "storage_free_gib": disk["free_gib"],
            "storage_free_percent": disk["free_percent"],
            "storage_min_free_percent": config.storage_min_free_percent,
            "storage_target_free_percent": config.storage_target_free_percent,
            "storage_used_percent": storage_used_percent,
            "storage_level": storage_level,

            "camera_model": status.camera_model,
            "camera_resolution": status.camera_resolution,

            "image_count": storage.image_count(),

            "event_count": len(events),
            "latest_event": latest_event,

            "birdpi_running": service.running(),

            "runtime_mode": status.mode,
            "runtime_ir_mode": status.ir_mode,
            "motion_active": status.motion_active,
            "current_event_id": status.current_event_id,
            "last_event_id": status.last_event_id,
            "runtime_last_update": runtime_last_update,

            "status_refresh_seconds": config.web.refresh_interval_seconds,

            "manual_video_active": status.manual_video_active,
        }

    @web.get("/")
    def index() -> str:
        latest_image = storage.latest_image()

        return render_template("index.html", latest_image=latest_image, )

    @web.get("/images/<path:filename>")
    def image(filename: str, ):
        return send_from_directory(storage.config.image_path, filename, )

    @web.get("/videos/<path:filename>")
    def video(filename: str, ):
        return send_from_directory(storage.config.video_path, filename, )

    @web.get("/gallery")
    def gallery() -> str:
        images = storage.images()

        return render_template("gallery.html", images=images, )

    @web.get("/gallery/<path:filename>")
    def gallery_image(filename: str, ) -> str:
        image = storage.get_image(
            filename
        )

        if image is None:
            abort(404)

        newer, older = storage.adjacent_images(
            image
        )

        return render_template("image.html",
                               image=image, newer=newer, older=older, )

    @web.get("/events")
    def events() -> str:
        motion_events = storage.events()

        return render_template("events.html", events=motion_events, )

    @web.get("/events/<event_id>")
    def event_detail(event_id: str, ) -> str:
        event = storage.event(event_id)

        if event is None:
            abort(404)

        return render_template("event.html", event=event, )

    @web.post("/service/start")
    def service_start():
        service.start()

        return redirect(
            url_for("web.index")
        )

    @web.post("/service/stop")
    def service_stop():
        service.stop()

        return redirect(url_for("web.index"))

    @web.post("/service/restart")
    def service_restart():
        service.restart()

        return redirect(url_for("web.index"))

    @web.post("/images/<path:filename>/delete")
    def delete_image(filename: str, ):
        storage.delete_image(filename)

        return redirect(url_for("web.gallery"))

    @web.post("/images/clear")
    def clear_images():
        storage.clear_images()

        return redirect(url_for("web.gallery"))

    @web.post("/videos/<path:filename>/delete")
    def delete_video(filename: str, ):
        storage.delete_video(filename)

        return redirect(url_for("web.events"))

    @web.post("/videos/clear")
    def clear_videos():
        storage.clear_videos()

        return redirect(url_for("web.events"))

    @web.post("/capture")
    def capture():
        runtime.capture_image()

        return redirect(url_for("web.index"))

    @web.post("/ir/off")
    def ir_off():
        runtime.ir_off()

        return redirect(url_for("web.index"))

    @web.post("/ir/left")
    def ir_left():
        runtime.ir_left()

        return redirect(url_for("web.index"))

    @web.post("/ir/right")
    def ir_right():
        runtime.ir_right()

        return redirect(url_for("web.index"))

    @web.post("/ir/both")
    def ir_both():
        runtime.ir_both()

        return redirect(url_for("web.index"))

    @web.post("/video/start")
    def video_start():
        runtime.video_start()

        return redirect(url_for("web.index"))

    @web.post("/video/stop")
    def video_stop():
        runtime.video_stop()

        return redirect(url_for("web.index"))

    return web
