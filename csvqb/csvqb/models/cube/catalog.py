"""
Catalog Metadata (base)
-----------------------
"""
from datetime import datetime
from typing import Optional, List
from abc import ABC

from csvqb.models.validationerror import ValidationError


class CatalogMetadataBase(ABC):
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        issued: Optional[datetime] = None,
    ):
        self.title: str = title
        self.description: Optional[str] = description
        self.issued: Optional[datetime] = issued

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this
