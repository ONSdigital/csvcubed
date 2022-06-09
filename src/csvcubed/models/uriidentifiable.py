"""
URI Identifiable
----------------
"""

import dataclasses
from typing import Optional
from abc import ABC, abstractmethod

from csvcubed.utils.uri import uri_safe


@dataclasses.dataclass
class UriIdentifiable(ABC):
    """
    Mixin which allows a class to represent something which is URI addressable.

    It allows the user to provide a `uri_safe_identifier_override` or neglect to provide one. If an override is not
    provided, then the string identifier returned by the abstract method `get_identifier` is turned into a URI-safe
    token which is returned by the `uri_safe_identifier` property.
    """

    @abstractmethod
    def get_identifier(self) -> str:
        """
        get_identifier - returns the property which is turned into a URI-safe identifier is no override is present.
        """
        pass

    @property
    @abstractmethod
    def uri_safe_identifier_override(self) -> Optional[str]:
        """An override for the URI-safe string which should be used to identify this object."""
        pass

    @uri_safe_identifier_override.setter
    @abstractmethod
    def uri_safe_identifier_override(self, value: Optional[str]) -> None:
        pass

    @property
    def uri_safe_identifier(self) -> str:
        """A URI-safe string which should be used to identify this object."""
        return self.uri_safe_identifier_override or uri_safe(self.get_identifier())

    @uri_safe_identifier.setter
    def uri_safe_identifier(self, uri_safe_identifier: str) -> None:
        self.uri_safe_identifier_override = uri_safe_identifier
