from dataclasses import replace

from birdpi.classification.classifier import Classifier
from birdpi.models import Observation


class DummyClassifier(Classifier):
    """
    Dummy classifier for testing the classification pipeline.
    """

    def classify(
            self,
            observation: Observation,
    ) -> Observation:
        return replace(
            observation,
            label="bird",
            confidence=0.95,
        )
