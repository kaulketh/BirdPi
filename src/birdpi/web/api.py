from flask import Flask

from birdpi.web.routes import register_routes


def create_app() -> Flask:
    """
    Create Flask application.
    """

    app = Flask(__name__)

    register_routes(app)

    return app
