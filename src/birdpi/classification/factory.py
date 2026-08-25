"""
Classifier factory for BirdPi.
"""

from birdpi.classification.classifier import Classifier
from birdpi.classification.dummy import DummyClassifier
from birdpi.config import Config


def create_classifier(config: Config) -> Classifier:
    """
    Create the configured classifier implementation.
    """

    match config.classifier_type:
        case "dummy":
            return DummyClassifier()

        case _:
            raise ValueError(
                f"Unknown classifier type: {config.classifier_type}"
            )