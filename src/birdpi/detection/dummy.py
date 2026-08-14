from datetime import datetime

from birdpi.detection.detector import Detector
from birdpi.models import CapturedImage, Observation


class DummyDetector(Detector):
    """
    Dummy detector for testing the detection pipeline.
    """

    def detect(
            self,
            image: CapturedImage,
    ) -> list[Observation]:
        """
        Return a simulated bird observation.
        """

        return [
            Observation(
                image=image,
                detected_at=datetime.now(),
                label="bird",
                confidence=0.93,
            )
        ]
