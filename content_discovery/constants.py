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
