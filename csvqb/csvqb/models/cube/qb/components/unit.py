"""
Units
-----
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC, abstractmethod
import pandas as pd

from csvqb.models.uriidentifiable import UriIdentifiable
from csvqb.models.validationerror import ValidationError
from .arbitraryrdf import ArbitraryRdf, TripleFragmentBase, RdfSerialisationHint
from .attribute import ExistingQbAttribute
from .datastructuredefinition import (
    QbDataStructureDefinition,
    MultiQbDataStructureDefinition,
)
from csvqb.inputs import pandas_input_to_columnar_str, PandasDataTypes


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
        self, data: pd.Series, column_title: str, output_uri_template: str
    ) -> List[ValidationError]:
        # todo: really need to move this check up a level since it may be necessary to consider output_uri_template too.
        return []  # TODO: implement this


QbUnitAttribute = ExistingQbAttribute(
    "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
)
