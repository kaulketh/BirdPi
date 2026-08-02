"""
Main application module for the BirdPi system.

This module defines the BirdPi class, the central hub for initializing and
running the BirdPi application. It integrates multiple components, including
configuration management and camera functionality, to provide the main
features of the application.
"""
from birdpi.camera.capture import Camera
from birdpi.config import Config


class BirdPi:
    """
    Main application class for the BirdPi system.
    """

    def __init__(self, config: Config):
        self.config = config
        self.camera = Camera(config)

    def run(self):
        """
        Start BirdPi application.
        """

        print("🐦 BirdPi online")

        image = self.camera.capture()

        print(f"📸 Image captured: {image}")
