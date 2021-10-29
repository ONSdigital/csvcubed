"""
Catalog Metadata (base)
-----------------------
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod

from csvcubed.models.pydanticmodel import PydanticModel


@dataclass
class CatalogMetadataBase(PydanticModel, ABC):
    title: str

    @abstractmethod
    def get_description(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_issued(self) -> Optional[datetime]:
        pass
