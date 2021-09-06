"""
Measures
--------
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC
import pandas as pd
import uritemplate

from csvqb.models.uriidentifiable import UriIdentifiable
from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .datastructuredefinition import (
    MultiQbDataStructureDefinition,
    QbDataStructureDefinition,
)
from .dimension import ExistingQbDimension
from csvqb.models.validationerror import ValidationError
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_str
from .validationerrors import UndefinedValuesError
from csvqb.utils.uri import csvw_column_name_safe, uri_safe
from csvqb.utils.validators.uri import validate_uri


@dataclass
class QbMeasure(QbDataStructureDefinition, ArbitraryRdf, ABC):
    pass


@dataclass
class ExistingQbMeasure(QbMeasure):
    measure_uri: str
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def __eq__(self, other):
        return (
            isinstance(other, ExistingQbMeasure)
            and self.measure_uri == other.measure_uri
        )

    def __hash__(self):
        return self.measure_uri.__hash__()

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Component

    _measure_uri_validator = validate_uri("measure_uri")


@dataclass
class NewQbMeasure(QbMeasure, UriIdentifiable):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    parent_measure_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def _get_identifiable_state(self) -> tuple:
        return (
            self.label,
            self.description,
            self.parent_measure_uri,
            self.uri_safe_identifier,
        )

    def __eq__(self, other):
        return (
            isinstance(other, NewQbMeasure)
            and self._get_identifiable_state() == other._get_identifiable_state()
        )

    def __hash__(self):
        return self._get_identifiable_state().__hash__()

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Component, RdfSerialisationHint.Property}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Property

    def get_identifier(self) -> str:
        return self.label


@dataclass
class QbMultiMeasureDimension(MultiQbDataStructureDefinition):
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

    def validate_data(
        self, data: pd.Series, csvw_column_name: str, csv_column_uri_template: str
    ) -> List[ValidationError]:
        if len(self.measures) > 0:
            unique_values = {uri_safe(v) for v in set(data.unique().flatten())}
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
                return [UndefinedValuesError(self, "measure URI", undefined_uris)]

        return []


QbMeasureTypeDimension = ExistingQbDimension(
    "http://purl.org/linked-data/cube#measureType",
    range_uri="http://purl.org/linked-data/cube#MeasureProperty",
)
