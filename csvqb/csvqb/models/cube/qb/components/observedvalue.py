from typing import Optional, List
import pandas as pd
from abc import ABC


from .component import QbMetaComponent, QbComponent
from .measure import QbMeasure, QbMeasureTypeDimension
from .attribute import QbUnitAttribute


class QbObservationValue(QbMetaComponent, ABC):
    data_type: str

    def __init__(self, data_type: str):
        self.data_type = data_type


class QbMultiMeasureObservationValue(QbObservationValue):
    def __init__(self, data_type: str = "number"):
        QbObservationValue.__init__(self, data_type)

    def validate(self) -> bool:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> bool:
        raise Exception("Not implemented yet")

    def get_qb_components(self) -> List[QbComponent]:
        return []


class QbSingleMeasureObservationValue(QbObservationValue):
    """
        Represents the unit/measure/datatype components necessary to define a simple qb:Observation.

        N.B. Requires `virt_unit` and `virt_measure` columns to be added to CSV-W metadata
    """

    measure: QbMeasure
    unit_uri: QbUnitAttribute

    def __init__(self,
                 measure: QbMeasure,
                 unit_uri: QbUnitAttribute,
                 data_type: Optional[str] = "number"):
        QbObservationValue.__init__(self, data_type)
        self.measure = measure
        self.unit_uri = unit_uri

    def validate(self) -> bool:
        raise Exception("Not implemented yet")

    def validate_data(self, data: pd.Series) -> bool:
        raise Exception("Not implemented yet")

    def get_qb_components(self) -> List[QbComponent]:
        return [self.measure, QbMeasureTypeDimension, self.unit_uri]
