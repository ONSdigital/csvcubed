"""
Units
-----

Represent units in an RDF Data Cube.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC

from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.utils.validators.attributes import enforce_optional_attribute_dependencies
from .arbitraryrdf import (
    ArbitraryRdf,
    TripleFragmentBase,
    RdfSerialisationHint,
)
from .datastructuredefinition import SecondaryQbStructuralDefinition
from csvcubed.utils.validators.uri import validate_uri


@dataclass
class QbUnit(SecondaryQbStructuralDefinition, ABC):
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

    _qudt_quantity_kind_uri_validation = validate_uri(
        "qudt_quantity_kind_uri", is_optional=True
    )

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        return self.arbitrary_rdf

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
