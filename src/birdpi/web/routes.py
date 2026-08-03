from flask import Flask


def register_routes(app: Flask) -> None:
    """
    Register all web routes.
    """

    @app.get("/")
    def index() -> str:
        return "BirdPi is running"
