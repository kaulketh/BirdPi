"""
Detection support for BirdPi.

This module provides the Detector class responsible for analyzing
captured images and creating observations.
"""

from birdpi.models import CapturedImage, Observation


class Detector:
    """
    Analyze captured images for observable objects.
    """

    def detect(
            self,
            image: CapturedImage,
    ) -> list[Observation]:
        """
        Analyze an image and return detected observations.
        """

        return []
