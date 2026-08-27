"""
Entry point for the complete BirdPi application.

This module is responsible for initializing and starting
the BirdPi application and the web UI by invoking main functions.
It acts as the gateway for running the program when executed as a standalone script.
"""
from birdpi import main, server

if __name__ == "__main__":
    main.main()
    server.main()
