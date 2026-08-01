from pathlib import Path
from birdpi import config
from birdpi.camera.capture import Camera


camera = Camera(
    Path(config.IMAGE_PATH)
)

image = camera.capture()

print(image)