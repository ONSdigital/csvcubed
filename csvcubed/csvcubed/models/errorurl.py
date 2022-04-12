"""
Csvcubed Error url specific funtionalities
------------------------------------------
"""

from abc import ABC, abstractmethod


class HasErrorUrl(ABC):
    """Abstract class representing the has error url model."""

    @classmethod
    @abstractmethod
    def get_error_url(cls) -> str:
        ...
