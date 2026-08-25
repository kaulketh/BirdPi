"""
Classification interface for BirdPi.
"""

from birdpi.models import Observation


class Classifier:
    """
    Base classifier for refining observations.
    """

    def classify(
        self,
        observation: Observation,
    ) -> Observation:
        """
        Classify an observation.

        The base implementation returns the observation unchanged.
        """

        return observation
    