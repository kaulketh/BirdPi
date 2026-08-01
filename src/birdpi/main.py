"""
The script initializes the BirdPi system, interfaces with a camera to
capture an image, and outputs relevant status and results.

This module is responsible for setting up and interacting with the
camera component of the BirdPi system to capture an image and save it
to a configured directory. It serves as the entry point for the BirdPi
system's functionality.
"""

from birdpi.camera.capture import Camera
from birdpi.config import IMAGE_PATH


def main():
    print("🐦 BirdPi online")

    camera = Camera(IMAGE_PATH)
    image = camera.capture()
    print(f"📸 Image captured: {image}")


if __name__ == "__main__":
    main()
