"""
Measures Dimension
------------------

Define a measure dimension in an RDF Data Cube.
"""

from dataclasses import dataclass
from typing import List

import pandas as pd
import uritemplate

from csvcubed.inputs import PandasDataTypes, pandas_input_to_columnar_str
from .measure import (
    QbMeasure,
    NewQbMeasure,
    ExistingQbMeasure,
)
from .validationerrors import UndefinedMeasureUrisError
from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.uri import uri_safe
from .datastructuredefinition import QbColumnStructuralDefinition


@dataclass
class QbMultiMeasureDimension(QbColumnStructuralDefinition):
    """
    Represents the measure types permitted in a multi-measure cube.
    """

    measures: List[QbMeasure]

    @staticmethod
    def new_measures_from_data(data: PandasDataTypes) -> "QbMultiMeasureDimension":
        columnar_data = pandas_input_to_columnar_str(data)
        return QbMultiMeasureDimension(
            [NewQbMeasure(m) for m in sorted(set(columnar_data))]
        )

    @staticmethod
    def existing_measures_from_data(
        data: PandasDataTypes, csvw_column_name: str, csv_column_uri_template: str
    ) -> "QbMultiMeasureDimension":
        columnar_data = pandas_input_to_columnar_str(data)
        return QbMultiMeasureDimension(
            [
                ExistingQbMeasure(
                    uritemplate.expand(csv_column_uri_template, {csvw_column_name: m})
                )
                for m in sorted(set(columnar_data))
            ]
        )

    def validate_data(
        self,
        data: pd.Series,
        csvw_column_name: str,
        csv_column_uri_template: str,
        column_csv_title: str,
    ) -> List[ValidationError]:
        if len(self.measures) > 0:
            unique_values = {uri_safe(v) for v in set(data.unique())}
            unique_expanded_uris = {
                uritemplate.expand(csv_column_uri_template, {csvw_column_name: s})
                for s in unique_values
            }
            expected_uris = set()
            for measure in self.measures:
                if isinstance(measure, ExistingQbMeasure):
                    expected_uris.add(measure.measure_uri)
                elif isinstance(measure, NewQbMeasure):
                    expected_uris.add(measure.uri_safe_identifier)
                else:
                    raise Exception(f"Unhandled measure type {type(measure)}")

            undefined_uris = unique_expanded_uris - expected_uris
            if len(undefined_uris) > 0:
                return [UndefinedMeasureUrisError(self, undefined_uris)]

        return []
