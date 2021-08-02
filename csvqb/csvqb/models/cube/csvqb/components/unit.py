"""
Units
-----
"""
from typing import Optional, List
from abc import ABC
import pandas as pd


from csvqb.utils.uri import uri_safe
from csvqb.models.validationerror import ValidationError
from .attribute import ExistingQbAttribute
from .datastructuredefinition import (
    QbDataStructureDefinition,
    MultiQbDataStructureDefinition,
)
from csvqb.inputs import pandas_input_to_columnar_str, PandasDataTypes


class QbUnit(QbDataStructureDefinition, ABC):
    def __init__(self, unit_multiplier: Optional[int]):
        self.unit_multiplier: Optional[int] = unit_multiplier


class ExistingQbUnit(QbUnit):
    def __init__(self, unit_uri: str, unit_multiplier: Optional[int] = None):
        QbUnit.__init__(self, unit_multiplier)
        self.unit_uri: str = unit_uri

    def __str__(self) -> str:
        unit_multiplier_str = (
            "" if self.unit_multiplier is None else f", 10^{self.unit_multiplier}"
        )
        return f"ExistingQbUnit('{self.unit_uri}'{unit_multiplier_str})"

    def validate(self) -> List[ValidationError]:
        return super(ExistingQbAttribute).validate()  # todo: Add more validation here.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return super(ExistingQbAttribute).validate_data(
            data
        )  # todo: Add more validation here.


class NewQbUnit(QbUnit):
    def __init__(
        self,
        label: str,
        uri_safe_identifier: Optional[str] = None,
        unit_multiplier: Optional[int] = None,
        description: Optional[str] = None,
        parent_unit_uri: Optional[str] = None,
        source_uri: Optional[str] = None,
    ):
        QbUnit.__init__(self, unit_multiplier)
        self.label: str = label
        self.uri_safe_identifier: str = (
            uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        )
        self.description: Optional[str] = description
        self.parent_unit_uri: Optional[str] = parent_unit_uri
        self.source_uri: Optional[str] = source_uri

    def __str__(self) -> str:
        return f"NewQbUnit('{self.label}')"

    def validate(self) -> List[ValidationError]:
        return super(ExistingQbAttribute).validate()  # todo: Add more validation here.

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return super(ExistingQbAttribute).validate_data(
            data
        )  # todo: Add more validation here.


class QbMultiUnits(MultiQbDataStructureDefinition):
    """
    Represents multiple units used/defined in a cube, typically used in multi-measure cubes.
    """

    def __init__(self, units: List[QbUnit]):
        self.units: List[QbUnit] = units

    def __str__(self) -> str:
        units_str = ",".join([str(u) for u in self.units])
        return f"QbMultiUnits({units_str})"

    @staticmethod
    def new_units_from_data(data: PandasDataTypes) -> "QbMultiUnits":
        """
        Automatically generates new units from a units column.
        """
        return QbMultiUnits(
            [NewQbUnit(u) for u in set(pandas_input_to_columnar_str(data))]
        )

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this

    def get_qb_components(self) -> List[QbDataStructureDefinition]:
        components: List[QbDataStructureDefinition] = [QbUnitAttribute]
        components += self.units
        return components


QbUnitAttribute = ExistingQbAttribute(
    "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
)
