"""
Catalog Metadata (base)
-----------------------
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional, Union

from csvcubed.models.validatedmodel import ValidatedModel, ValidationFunction
from csvcubed.utils import validations as v


@dataclass
class CatalogMetadataBase(ValidatedModel, ABC):
    title: str

    @abstractmethod
    def get_description(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_issued(self) -> Union[datetime, date, None]:
        pass

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {"title": v.string}
