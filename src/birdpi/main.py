"""
Main entry point for BirdPi.
"""
from birdpi.application import BirdPi
from birdpi.bootstrap import initialize


def main() -> None:
    config = initialize()

    birdpi = BirdPi(config)
    birdpi.run()


if __name__ == "__main__":
    main()
