"""
Units
-----
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC
import pandas as pd
import uritemplate

from csvqb.models.uriidentifiable import UriIdentifiable
from csvqb.models.validationerror import ValidationError
from csvqb.utils.validators.attributes import enforce_optional_attribute_dependencies
from .arbitraryrdf import ArbitraryRdf, TripleFragmentBase, RdfSerialisationHint
from .attribute import ExistingQbAttribute
from .datastructuredefinition import (
    QbDataStructureDefinition,
    MultiQbDataStructureDefinition,
)
from csvqb.inputs import pandas_input_to_columnar_str, PandasDataTypes
from .validationerrors import UndefinedValuesError
from csvqb.utils.uri import uri_safe
from csvqb.utils.validators.uri import validate_uri


@dataclass
class QbUnit(QbDataStructureDefinition, ABC):
    pass


@dataclass
class ExistingQbUnit(QbUnit):
    unit_uri: str

    _unit_uri_validator = validate_uri("unit_uri")

    def __eq__(self, other):
        return isinstance(other, ExistingQbUnit) and other.unit_uri == self.unit_uri

    def __hash__(self):
        return self.unit_uri.__hash__()


@dataclass
class NewQbUnit(QbUnit, UriIdentifiable, ArbitraryRdf):
    label: str
    description: Optional[str] = field(default=None, repr=False)
    source_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    base_unit: Optional[QbUnit] = field(default=None, repr=False)
    """
    The unit that this new unit is based on.
    
    Codependent with :attr:`base_unit_scaling_factor`.
    """
    base_unit_scaling_factor: Optional[float] = field(default=None, repr=False)
    """
    How to scale the value associated with this unit to map back to the base unit.
    
    Codependent with :attr:`base_unit`.
    
    e.g. if the base unit is *meters* and this unit (*kilometers*) has a scaling factor of **1,000**, then you multiply 
    the value in *kilometers* by **1,000** to get the value in *meters*.    
    """

    qudt_quantity_kind_uri: Optional[str] = field(default=None, repr=False)
    """
    The URI of the `qudt:QuantityKind` family to which this unit belongs.
    
    Codependent with :attr:`si_base_unit_conversion_multiplier`. 
    """
    si_base_unit_conversion_multiplier: Optional[float] = field(
        default=None, repr=False
    )
    """
    Multiply a value by this number to convert between this unit and its corresponding **SI unit**.

    Codependent with :attr:`qudt_quantity_kind_uri`. 
       
    See https://github.com/qudt/qudt-public-repo/wiki/User-Guide-for-QUDT#4-conversion-multipliers-in-qudt to understand
    the role of `qudt:conversionMultiplier` before using this. *It may not represent what you think it does.*
    
    SI - https://en.wikipedia.org/wiki/International_System_of_Units 
    """

    optional_attribute_dependencies = enforce_optional_attribute_dependencies(
        {
            "base_unit": ["base_unit_scaling_factor"],
            "base_unit_scaling_factor": ["base_unit"],
            "si_base_unit_conversion_multiplier": ["qudt_quantity_kind_uri"],
            "qudt_quantity_kind_uri": ["si_base_unit_conversion_multiplier"],
        }
    )

    _qudt_quantity_kind_uri_validation = validate_uri("qudt_quantity_kind_uri")

    def _get_identifiable_state(self) -> tuple:
        """
        Used in hash calculation and equality comparisons.

        :return: The properties which make this unit unique.
        """
        return (
            self.label,
            self.description,
            self.base_unit,
            self.uri_safe_identifier,
        )

    def __eq__(self, other):
        return (
            isinstance(other, NewQbUnit)
            and self._get_identifiable_state() == other._get_identifiable_state()
        )

    def __hash__(self):
        return self._get_identifiable_state().__hash__()

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
        self, data: pd.Series, csvw_column_name: str, csv_column_uri_template: str
    ) -> List[ValidationError]:
        if len(self.units) > 0:
            unique_values = {uri_safe(v) for v in set(data.unique().flatten())}
            unique_expanded_uris = {
                uritemplate.expand(csv_column_uri_template, {csvw_column_name: s})
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
                return [UndefinedValuesError(self, "unit URI", undefined_uris)]

        return []


QbUnitAttribute = ExistingQbAttribute(
    "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
)
