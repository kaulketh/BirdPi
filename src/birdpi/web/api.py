"""
Create and configure the BirdPi Flask web application.
"""

from pathlib import Path

from flask import (
    Flask,
    render_template,
)

from birdpi.config import Config
from birdpi.exceptions import (
    RuntimeCommandError,
    ServiceControlError,
)
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger
from birdpi.web.routes import register_routes

logger = get_logger(__name__)


def create_app(
        config: Config,
        storage: Storage,
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

    @app.errorhandler(RuntimeCommandError)
    def handle_runtime_command_error(
            error: RuntimeCommandError,
    ):
        logger.warning(
            "WebUI runtime command failed: %s",
            error,
        )

        return (
            render_template(
                "error.html",
                title="Runtime unavailable",
                message=(
                    "The BirdPi runtime service "
                    "is currently not reachable."
                ),
            ),
            503,
        )

    @app.errorhandler(ServiceControlError)
    def handle_service_control_error(
            error: ServiceControlError,
    ):
        logger.warning(
            "WebUI service control failed: %s",
            error,
        )

        return (
            render_template(
                "error.html",
                title="Service control failed",
                message=(
                    "BirdPi could not perform "
                    "the requested service action."
                ),
            ),
            503,
        )

    web = register_routes(
        config=config,
        storage=storage,
    )

    app.register_blueprint(web)

    return app
