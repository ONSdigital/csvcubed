from typing import Optional, List
from abc import ABC

import pandas as pd

from csvqb.utils.uri import uri_safe
from .datastructuredefinition import MultiQbDataStructureDefinition, QbDataStructureDefinition
from .dimension import ExistingQbDimension
from csvqb.models.validationerror import ValidationError


class QbMeasure(QbDataStructureDefinition, ABC):
    pass


class ExistingQbMeasure(QbMeasure):
    def __init__(self, measure_uri: str):
        QbMeasure.__init__(self)
        self.measure_uri: str = measure_uri

    def __str__(self) -> str:
        return f"ExistingQbMeasure('{self.measure_uri}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class NewQbMeasure(QbMeasure):
    def __init__(self,
                 label: str,
                 description: Optional[str] = None,
                 uri_safe_identifier: Optional[str] = None,
                 parent_measure_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        QbMeasure.__init__(self)
        self.label: str = label
        self.description: Optional[str] = description
        self.uri_safe_identifier: str = uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        self.parent_measure_uri: Optional[str] = parent_measure_uri
        self.source_uri: Optional[str] = source_uri

    def __str__(self) -> str:
        return f"NewQbMeasure('{self.label}')"

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class QbMultiMeasureDimension(MultiQbDataStructureDefinition):
    """
        Represents the measure types permitted in a multi-measure cube.
    """
    def __init__(self, measures: List[QbMeasure]):
        self.measures: List[QbMeasure] = measures

    def __str__(self) -> str:
        measures_str = ", ".join([str(m) for m in self.measures])
        return f"QbMultiMeasureDimension({measures_str})"

    @staticmethod
    def new_measures_from_data(data: pd.Series) -> "QbMultiMeasureDimension":
        return QbMultiMeasureDimension([NewQbMeasure(m) for m in sorted(set(data))])

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this

    def get_qb_components(self) -> List[QbDataStructureDefinition]:
        components: List[QbDataStructureDefinition] = [QbMeasureTypeDimension]
        components += self.measures
        return components


QbMeasureTypeDimension = ExistingQbDimension("http://purl.org/linked-data/cube#measureType",
                                             range_uri="http://purl.org/linked-data/cube#MeasureProperty")
