"""
Units
-----
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC, abstractmethod
import pandas as pd
import uritemplate

from csvqb.models.uriidentifiable import UriIdentifiable
from csvqb.models.validationerror import ValidationError
from .arbitraryrdf import ArbitraryRdf, TripleFragmentBase, RdfSerialisationHint
from .attribute import ExistingQbAttribute
from .datastructuredefinition import (
    QbDataStructureDefinition,
    MultiQbDataStructureDefinition,
)
from csvqb.inputs import pandas_input_to_columnar_str, PandasDataTypes
from .validationerrors import UndefinedValuesError


@dataclass
class QbUnit(QbDataStructureDefinition, ABC):
    @abstractmethod
    def unit_multiplier(self) -> Optional[int]:
        pass


@dataclass
class ExistingQbUnit(QbUnit):
    unit_uri: str
    unit_multiplier: Optional[int] = field(default=None, repr=False)


@dataclass
class NewQbUnit(QbUnit, UriIdentifiable, ArbitraryRdf):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    unit_multiplier: Optional[int] = field(default=None, repr=False)
    parent_unit_uri: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {RdfSerialisationHint.Unit}

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.Unit

    def get_identifier(self) -> str:
        return self.label


@dataclass
class QbMultiUnits(MultiQbDataStructureDefinition):
    """
    Represents multiple units used/defined in a cube, typically used in multi-measure cubes.
    """

    units: List[QbUnit]

    @staticmethod
    def new_units_from_data(data: PandasDataTypes) -> "QbMultiUnits":
        """
        Automatically generates new units from a units column.
        """
        return QbMultiUnits(
            [NewQbUnit(u) for u in set(pandas_input_to_columnar_str(data))]
        )

    def validate_data(
        self, data: pd.Series, csv_column_name: str, output_uri_template: str
    ) -> List[ValidationError]:
        if len(self.units) > 0:
            unique_values = set(data.unique().flatten())
            unique_expanded_uris = {
                uritemplate.expand(output_uri_template, {csv_column_name: s})
                for s in unique_values
            }
            expected_uris = set()
            for unit in self.units:
                if isinstance(unit, ExistingQbUnit):
                    expected_uris.add(unit.unit_uri)
                elif isinstance(unit, NewQbUnit):
                    expected_uris.add(unit.uri_safe_identifier)
                else:
                    raise Exception(f"Unhandled unit type {type(unit)}")

            undefined_uris = unique_expanded_uris - expected_uris
            if len(undefined_uris) > 0:
                return [UndefinedValuesError(self, undefined_uris)]

        return []


QbUnitAttribute = ExistingQbAttribute(
    "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
)
