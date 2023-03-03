"""
Catalog Metadata (base)
-----------------------
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Union

from csvcubed.models.pydanticmodel import PydanticModel
from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction


@dataclass
class CatalogMetadataBase(PydanticModel, ValidatedModel, ABC):
    title: str

    @abstractmethod
    def get_description(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_issued(self) -> Union[datetime, date, None]:
        pass
