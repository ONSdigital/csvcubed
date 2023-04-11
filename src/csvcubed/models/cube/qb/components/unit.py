"""
Units
-----

Represent units in an RDF Data Cube.
"""
import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union

from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import (
    ValidatedModel,
    ValidationFunction,
    Validations,
)
from csvcubed.models.validationerror import ValidateModelPropertiesError
from csvcubed.utils import validations as v

from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .datastructuredefinition import SecondaryQbStructuralDefinition

_logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class QbUnit(SecondaryQbStructuralDefinition, ABC):
    pass


@dataclass
class ExistingQbUnit(QbUnit):
    unit_uri: str

    def __eq__(self, other):
        return isinstance(other, ExistingQbUnit) and other.unit_uri == self.unit_uri

    def __hash__(self):
        return self.unit_uri.__hash__()

    def _get_validations(self) -> Union[Validations, Dict[str, ValidationFunction]]:
        return {"unit_uri": v.uri}


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

    def _get_validations(self) -> Union[Validations, Dict[str, ValidationFunction]]:
        return Validations(
            individual_property_validations={
                "label": v.string,
                "description": v.optional(v.string),
                "source_uri": v.optional(v.uri),
                **UriIdentifiable._get_validations(self),
                "arbitrary_rdf": v.list(v.validated_model(TripleFragmentBase)),
                "base_unit": v.optional(v.validated_model(QbUnit)),
                "base_unit_scaling_factor": v.optional(v.float),
                "qudt_quantity_kind_uri": v.optional(v.uri),
                "si_base_unit_conversion_multiplier": v.optional(v.float),
            },
            whole_object_validations=[
                self._validation_base_unit_scaling_factor_dependency
            ],
        )

    @staticmethod
    def _validation_base_unit_scaling_factor_dependency(
        unit: "NewQbUnit", property_path: List[str]
    ) -> List[ValidateModelPropertiesError]:
        errors: List[ValidateModelPropertiesError] = []

        if unit.base_unit_scaling_factor is not None and unit.base_unit is None:
            errors.append(
                ValidateModelPropertiesError(
                    f"A value for base unit scaling factor has been specified: '{unit.base_unit_scaling_factor}' but no value for base unit has been specified and must be provided.",
                    property_path,
                    unit,
                )
            )

        if (
            unit.si_base_unit_conversion_multiplier is not None
            and unit.qudt_quantity_kind_uri is None
        ):
            errors.append(
                ValidateModelPropertiesError(
                    f"A value for si base unit conversion multiplier has been specified: '{unit.si_base_unit_conversion_multiplier}' but no value for QUDT quantity kind URL has been specified and must be provided.",
                    property_path,
                    unit,
                )
            )
        return errors

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
