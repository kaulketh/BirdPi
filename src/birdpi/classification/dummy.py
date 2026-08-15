"""
Dummy classifier for testing the BirdPi classification pipeline.
"""

from birdpi.classification.classifier import Classifier
from birdpi.models import Observation


class DummyClassifier(Classifier):
    """
    Simulate classification of an observation.
    """

    def classify(
        self,
        observation: Observation,
    ) -> Observation:
        observation.classification_label = "bird"
        observation.classification_confidence = 0.95

        return observation