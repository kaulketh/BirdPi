from birdpi.camera.capture import Camera
from birdpi.config import IMAGE_PATH


class BirdPi:
    """
    Main application class for the BirdPi system.
    """

    def __init__(self):
        self.camera = Camera(IMAGE_PATH)

    def run(self):
        """
        Start BirdPi application.
        """

        print("🐦 BirdPi online")

        image = self.camera.capture()

        print(f"📸 Image captured: {image}")