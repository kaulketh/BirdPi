"""A module for representing geographic locations.

This module provides a data structure for storing geographic coordinates,
and a predefined dictionary of named locations using the `Location` class.
Locations are immutable and use efficient memory representation.

"""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Location:
    latitude: float
    longitude: float


LOCATIONS = {
    "HOME": Location(
        latitude=52.1437,
        longitude=14.6419,
    ),
}
