"""
A module for controlling and managing infrared (IR) lights using GPIO pins.

This module provides an enumeration for IR light modes and a class to
manipulate the state of IR lights, including turning them on, off, and
specifying which light(s) should be active.
"""
from enum import Enum

from gpiozero import DigitalOutputDevice


class IRMode(Enum):
    OFF = "off"
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


class IRLights:
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

        self._mode = IRMode.OFF

    @property
    def mode(self) -> IRMode:
        return self._mode

    def set_mode(
            self,
            mode: IRMode,
    ) -> None:
        match mode:
            case IRMode.OFF:
                self.left.off()
                self.right.off()

            case IRMode.LEFT:
                self.left.on()
                self.right.off()

            case IRMode.RIGHT:
                self.left.off()
                self.right.on()

            case IRMode.BOTH:
                self.left.on()
                self.right.on()

        self._mode = mode

    def on(self) -> None:
        self.set_mode(IRMode.BOTH)

    def off(self) -> None:
        self.set_mode(IRMode.OFF)

    def left_on(self) -> None:
        self.set_mode(IRMode.LEFT)

    def right_on(self) -> None:
        self.set_mode(IRMode.RIGHT)

    def close(self) -> None:
        self.off()
        self.left.close()
        self.right.close()

    def __enter__(self) -> "IRLights":
        return self

    def __exit__(self, *args) -> None:
        self.close()
