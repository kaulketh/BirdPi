"""
The main application module of the BirdPi system.

This module serves as the entry point for the BirdPi application. It sets up
and manages the core components such as configuration, storage, camera, detector,
and observer. It also provides methods to execute the key functionalities of the
application, including image capture, observation, and session management.
"""

from birdpi.camera.capture import Camera
from birdpi.classification.classifier import Classifier
from birdpi.classification.factory import create_classifier
from birdpi.config import Config
from birdpi.detection.detector import Detector
from birdpi.detection.factory import (
    create_detector,
    create_object_detector,
)
from birdpi.models import CapturedImage
from birdpi.observer import Observer
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class BirdPi:
    """
    Main application class for the BirdPi system.
    """

    def __init__(
            self,
            config: Config,
            detector: Detector | None = None,
            classifier: Classifier | None = None,
    ) -> None:
        self.config = config

        self.storage = Storage(config)
        self.storage.ensure_directories()

        self.camera = Camera(config)

        self.detector = detector or create_detector(config)
        self.object_detector = create_object_detector(config)
        self.classifier = classifier or create_classifier(config)

        self.observer = Observer(
            config,
            self.capture,
        )

    def run(self) -> None:
        """
        Start BirdPi application.
        """

        logger.info("BirdPi online")
        image = self.camera.capture()
        logger.info("Image captured: %s", image.path)

    def start_observation(self) -> None:
        """
        Start automatic observation.
        """

        self.observer.start()

    def stop_observation(self) -> None:
        """
        Stop automatic observation and persist the completed session.
        """

        self.observer.stop()

        session = self.observer.session

        if session is not None and not session.active:
            path = self.storage.save_session(session)

            logger.info(
                "Observation session saved: %s",
                path,
            )

    def capture(
            self,
            session_id: str | None = None,
    ) -> CapturedImage:
        """

        Capture an image, run detection, classify, and persist observations.
        """

        image = self.camera.capture(
            session_id=session_id,
        )

        observations = self.detector.detect(image)

        for observation in observations:
            observation.objects = self.object_detector.detect(
                image
            )

            self.classifier.classify(observation)

            self.storage.save_observation(observation)

        logger.info(
            "Detections: %s",
            len(observations),
        )
        logger.info(
            "Image captured: %s",
            image.path,
        )

        return image
