from typing import Optional, List
from abc import ABC

import pandas as pd

from .component import QbMetaComponent, QbComponent
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
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        raise Exception("Not implemented yet")


class NewQbMeasure(QbMeasure):
    label: str
    description: Optional[str]
    parent_measure_uri: Optional[str]
    source_uri: Optional[str]

    def __init__(self,
                 label: str,
                 description: Optional[str] = None,
                 parent_measure_uri: Optional[str] = None,
                 source_uri: Optional[str] = None):
        QbMeasure.__init__(self)
        self.label = label
        self.description = description
        self.parent_measure_uri = parent_measure_uri
        self.source_uri = source_uri

    def validate(self) -> List[ValidationError]:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        raise Exception("Not implemented yet")


class QbMultiMeasureTypes(QbMetaComponent):
    """
        Represents the measure types permitted in a multi-measure cubes.
    """

    measures: List[QbMeasure]

    def __init__(self, measures: List[QbMeasure]):
        self.measures = measures

    def validate(self) -> List[ValidationError]:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> List[ValidationError]:
        raise Exception("Not implemented yet")

    def get_qb_components(self) -> List[QbComponent]:
        components: List[QbComponent] = [QbMeasureTypeDimension]
        components += self.measures
        return components


QbMeasureTypeDimension = ExistingQbDimension("http://purl.org/linked-data/cube#measureType",
                                             range_uri="http://purl.org/linked-data/cube#MeasureProperty")
