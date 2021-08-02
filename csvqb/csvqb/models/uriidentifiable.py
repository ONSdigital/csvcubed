import dataclasses
from typing import Optional
from abc import ABC, abstractmethod

from csvqb.utils.uri import uri_safe


@dataclasses.dataclass
class UriIdentifiable(ABC):
    """Requires that implementing classes provide callers with a way of overriding the uri_safe_identifier property."""

    @abstractmethod
    def get_identifier(self) -> str:
        """
        get_identifier - returns the property which is turned into a URI-safe identifier is no override is present.
        """
        pass

    @property
    @abstractmethod
    def uri_safe_identifier_override(self) -> Optional[str]:
        pass

    @uri_safe_identifier_override.setter
    @abstractmethod
    def uri_safe_identifier_override(self, value: Optional[str]) -> None:
        pass

    @property
    def uri_safe_identifier(self) -> str:
        return self.uri_safe_identifier_override or uri_safe(self.get_identifier())

    @uri_safe_identifier.setter
    def uri_safe_identifier(self, uri_safe_identifier: str) -> None:
        self.uri_safe_identifier_override = uri_safe_identifier
