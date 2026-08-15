"""
Classification support for BirdPi.
"""

from birdpi.models import Observation


class Classifier:
    """
    Refine an observation with a classification result.
    """

    def classify(
            self,
            observation: Observation,
    ) -> Observation:
        """
        Classify an observation and return the refined result.
        """

        return observation
