"""
Control the BirdPi infrared lights.
"""

from enum import Enum

from gpiozero import DigitalOutputDevice


class IRMode(Enum):
    OFF = "off"
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class IRLights:
    """
    Control the left and right infrared lights.
    """

    def __init__(
            self,
            left_pin: int,
            right_pin: int,
    ) -> None:
        self.left = DigitalOutputDevice(
            left_pin,
            initial_value=False,
        )

        self.right = DigitalOutputDevice(
            right_pin,
            initial_value=False,
        )

    def set_mode(
            self,
            mode: IRMode,
    ) -> None:
        match mode:
            case IRMode.OFF:
                self.off()

            case IRMode.LEFT:
                self.left_on()
                self.right_off()

            case IRMode.RIGHT:
                self.left_off()
                self.right_on()

            case IRMode.BOTH:
                self.on()

    def on(self) -> None:
        self.left.on()
        self.right.on()

    def off(self) -> None:
        self.left.off()
        self.right.off()

    def left_on(self) -> None:
        self.left.on()

    def left_off(self) -> None:
        self.left.off()

    def right_on(self) -> None:
        self.right.on()

    def right_off(self) -> None:
        self.right.off()

    def close(self) -> None:
        self.off()
        self.left.close()
        self.right.close()

    def __enter__(self) -> "IRLights":
        return self

    def __exit__(self, *args) -> None:
        self.close()
