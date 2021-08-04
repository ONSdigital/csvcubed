"""
Units
-----
"""
from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC, abstractmethod
import pandas as pd

from csvqb.models.uriidentifiable import UriIdentifiable
from csvqb.models.validationerror import ValidationError
from .attribute import ExistingQbAttribute
from .datastructuredefinition import (
    QbDataStructureDefinition,
    MultiQbDataStructureDefinition,
)
from csvqb.inputs import pandas_input_to_columnar_str, PandasDataTypes


@dataclass
class QbUnit(QbDataStructureDefinition, ABC):
    @abstractmethod
    def unit_multiplier(self) -> Optional[int]:
        pass


@dataclass
class ExistingQbUnit(QbUnit):
    unit_uri: str
    unit_multiplier: Optional[int] = field(default=None, repr=False)

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # todo: Add more validation here.


@dataclass
class NewQbUnit(QbUnit, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    unit_multiplier: Optional[int] = field(default=None, repr=False)
    parent_unit_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.label

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # todo: Add more validation here.


@dataclass
class QbMultiUnits(MultiQbDataStructureDefinition):
    """
    Represents multiple units used/defined in a cube, typically used in multi-measure cubes.
    """
    units: List[QbUnit]

    @staticmethod
    def new_units_from_data(data: PandasDataTypes) -> "QbMultiUnits":
        """
        Automatically generates new units from a units column.
        """
        return QbMultiUnits(
            [NewQbUnit(u) for u in set(pandas_input_to_columnar_str(data))]
        )

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this


QbUnitAttribute = ExistingQbAttribute(
    "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
)
