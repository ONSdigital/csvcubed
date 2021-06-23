from typing import Optional, List
from abc import ABC

import pandas as pd

from csvqb.utils.uri import uri_safe
from .datastructuredefinition import MultiQbDataStructureDefinition, QbDataStructureDefinition
from .dimension import QbDimension, ExistingQbDimension
from csvqb.models.validationerror import ValidationError


class QbMeasure(QbDimension, ABC):
    def __init__(self):
        QbDimension.__init__(self, None)


class ExistingQbMeasure(QbMeasure):
    measure_uri: str

    def __init__(self, measure_uri: str):
        QbMeasure.__init__(self)
        self.measure_uri = measure_uri

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class NewQbMeasure(QbMeasure):
    label: str
    uri_safe_identifier: str
    description: Optional[str]
    parent_measure_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 description: Optional[str] = None,
                 uri_safe_identifier: Optional[str] = None,
                 parent_measure_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        QbMeasure.__init__(self)
        self.label = label
        self.description = description
        self.uri_safe_identifier = uri_safe_identifier if uri_safe_identifier is not None else uri_safe(label)
        self.parent_measure_uri = parent_measure_uri
        self.source_uri = source_uri

    def validate(self) -> List[ValidationError]:
        return []  # TODO: implement this

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        return []  # TODO: implement this


class QbMultiMeasureTypes(MultiQbDataStructureDefinition):
    """
        Represents the measure types permitted in a multi-measure cubes.
    """

    measures: List[QbMeasure]

    def __init__(self, measures: List[QbMeasure]):
        self.measures = measures

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
