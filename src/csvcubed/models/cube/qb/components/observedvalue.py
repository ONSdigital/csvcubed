"""
Observed Values
---------------

Represent observed values in an RDF Data Cube.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

from csvcubed.models.validatedmodel import ValidationFunction
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils import validations as v

from .datastructuredefinition import QbColumnStructuralDefinition
from .measure import QbMeasure
from .unit import QbUnit


@dataclass
class QbObservationValue(QbColumnStructuralDefinition):
    """
    Represents the unit/measure/datatype components necessary to define a simple qb:Observation.

    N.B. Requires `virt_unit` and `virt_measure` columns to be added to CSV-W metadata
    """

    measure: Optional[QbMeasure] = None
    unit: Optional[QbUnit] = None
    data_type: str = field(default="decimal", repr=False)

    @property
    def is_pivoted_shape_observation(self) -> bool:
        """
        Returns whether this observation is being represented in a pivoted or standard shape cube.
        """
        return self.measure is not None

    def validate_data(
        self,
        data: pd.Series,
        column_csvw_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        return []

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            "measure": v.optional(v.validated_model(QbMeasure)),
            "unit": v.optional(v.validated_model(QbUnit)),
            "data_type": v.any_of(v.data_type, v.uri),
        }
