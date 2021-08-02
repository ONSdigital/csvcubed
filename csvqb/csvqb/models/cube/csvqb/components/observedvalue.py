"""
Observed Values
---------------
"""
from typing import Optional, List
import pandas as pd
from abc import ABC


from .datastructuredefinition import (
    MultiQbDataStructureDefinition,
    QbDataStructureDefinition,
)
from .measure import QbMeasure, QbMeasureTypeDimension
from .unit import QbUnit, QbUnitAttribute
from csvqb.models.validationerror import ValidationError


class QbObservationValue(MultiQbDataStructureDefinition, ABC):
    def __init__(self, data_type: Optional[str], unit: Optional[QbUnit]):
        self.data_type: str = data_type if data_type is not None else "decimal"
        self.unit: Optional[QbUnit] = unit


class QbMultiMeasureObservationValue(QbObservationValue):
    def __init__(self, data_type: Optional[str] = None, unit: Optional[QbUnit] = None):
        """

        :param data_type: Data type of the observed value.
        :param unit: Optional. Only defined where all measures in the cube have the same unit.
        """
        QbObservationValue.__init__(self, data_type, unit)

    def __str__(self) -> str:
        units_str = "" if self.unit is None else f", {self.unit}"
        return f"QbMultiMeasureObservationValue('{self.data_type}'{units_str})"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this

    def get_qb_components(self) -> List[QbDataStructureDefinition]:
        return []


class QbSingleMeasureObservationValue(QbObservationValue):
    """
    Represents the unit/measure/datatype components necessary to define a simple qb:Observation.

    N.B. Requires `virt_unit` and `virt_measure` columns to be added to CSV-W metadata
    """

    def __init__(
        self,
        measure: QbMeasure,
        unit: Optional[QbUnit] = None,
        data_type: Optional[str] = None,
    ):
        QbObservationValue.__init__(self, data_type, unit)
        self.measure: QbMeasure = measure

    def __str__(self) -> str:
        units_str = "" if self.unit is None else f", {self.unit}"
        return f"QbMultiMeasureObservationValue({self.measure}{units_str})"

    def validate(self) -> List[ValidationError]:
        errors: List[ValidationError] = []
        if self.measure is None:
            errors.append(ValidationError(f"{self} - no measure has been defined."))

        return errors

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this

    def get_qb_components(self) -> List[QbDataStructureDefinition]:
        components = [self.measure, QbMeasureTypeDimension]
        if self.unit is not None:
            components += [self.unit, QbUnitAttribute]

        return components
