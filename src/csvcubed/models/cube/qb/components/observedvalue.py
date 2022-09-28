"""
Observed Values
---------------

Represent observed values in an RDF Data Cube.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC, abstractmethod
import pandas as pd

from .datastructuredefinition import QbColumnStructuralDefinition
from .measure import QbMeasure
from .unit import QbUnit
from csvcubed.models.validationerror import ValidationError


@dataclass
class QbObservationValue(QbColumnStructuralDefinition, ABC):
    @property
    @abstractmethod
    def data_type(self) -> str:
        pass

    @data_type.setter
    @abstractmethod
    def data_type(self, value: str):
        pass

    @property
    @abstractmethod
    def unit(self) -> Optional[QbUnit]:
        pass

    @unit.setter
    @abstractmethod
    def unit(self, value: Optional[QbUnit]):
        pass


@dataclass
class QbMultiMeasureObservationValue(QbObservationValue):
    data_type: str = field(default="decimal", repr=False)
    unit: Optional[QbUnit] = None

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        return []  # TODO: implement this


@dataclass
class QbSingleMeasureObservationValue(QbObservationValue):
    """
    Represents the unit/measure/datatype components necessary to define a simple qb:Observation.

    N.B. Requires `virt_unit` and `virt_measure` columns to be added to CSV-W metadata
    """

    measure: QbMeasure
    unit: Optional[QbUnit] = None
    data_type: str = field(default="decimal", repr=False)

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        return []  # TODO: implement this
