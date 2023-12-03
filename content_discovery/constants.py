from enum import Enum


class Visibility(Enum):
    """Enum for the visibility of a snap"""

    PUBLIC = 1
    PRIVATE = 2


class Privacy(Enum):
    """Enum for privacy of a snap"""

    PUBLIC = 1
    FOLLOWERS = 2

    @staticmethod
    def validate(value: int) -> None:
        """Validates privacy"""
        if value not in {item.value for item in Privacy}:
            raise ValueError("Invalid privacy setting")


class Frequency(Enum):
    """Enum for periods of time to measure frequency of snap posting"""

    per_minute = "per_minute"
    hourly = "hourly"
    daily = "daily"
    monthly = "monthly"
