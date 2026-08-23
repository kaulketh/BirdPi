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

        birds = [
            obj
            for obj in observation.objects
            if obj.label == "bird"
        ]

        if birds:
            observation.classification_label = "bird"
            observation.classification_confidence = max(
                obj.confidence
                for obj in birds
            )
        else:
            observation.classification_label = "not_bird"
            observation.classification_confidence = None

        return observation
