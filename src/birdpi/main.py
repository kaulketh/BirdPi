"""
Entry point for the BirdPi application.

This module initializes the BirdPi application and triggers its execution.
The BirdPi application is designed to manage and interact with hardware
or systems related to bird monitoring or tracking.

Functions:
    main(): Initializes and runs the BirdPi application.
"""
from birdpi.application import BirdPi


def main():
    app = BirdPi()
    app.run()


if __name__ == "__main__":
    main()