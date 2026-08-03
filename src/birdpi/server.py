"""
Entry point for running the BirdPi web application.

This module initializes the BirdPi web application using the `create_app`
function and runs the application on the specified host and port.

"""
from birdpi.web.api import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
