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
from csvcubed.utils.validations import (
    validate_float_type,
    validate_list,
    validate_optional,
    validate_str_type,
    validate_uri,
)
from csvcubed.utils.validators.attributes import (
    enforce_optional_attribute_dependencies as pydantic_enforce_optional_attribute_dependencies,
)
from csvcubed.utils.validators.uri import validate_uri as pydantic_validate_uri

from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .datastructuredefinition import SecondaryQbStructuralDefinition

_logger = logging.getLogger(__name__)


@dataclass(unsafe_hash=True)
class QbUnit(SecondaryQbStructuralDefinition, ABC):
    pass


@dataclass
class ExistingQbUnit(QbUnit):
    unit_uri: str

    _unit_uri_validator = pydantic_validate_uri("unit_uri")

    def __eq__(self, other):
        return isinstance(other, ExistingQbUnit) and other.unit_uri == self.unit_uri

    def __hash__(self):
        return self.unit_uri.__hash__()

    def _get_validations(self) -> Union[Validations, Dict[str, ValidationFunction]]:
        return {"unit_uri": validate_uri}


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
                "label": validate_str_type,
                "description": validate_optional(validate_str_type),
                "source_uri": validate_optional(validate_uri),
                **UriIdentifiable._get_validations(self),
                "arbitrary_rdf": validate_list(v.validated_model(TripleFragmentBase)),
                "base_unit": validate_optional(v.validated_model(QbUnit)),
                "base_unit_scaling_factor": validate_optional(validate_float_type),
                "qudt_quantity_kind_uri": validate_optional(validate_uri),
                "si_base_unit_conversion_multiplier": validate_optional(
                    validate_float_type
                ),
            },
            whole_object_validations=[
                self._validation_base_unit_scaling_factor_dependency
            ],
        )

    @staticmethod
    def _validation_base_unit_scaling_factor_dependency(
        unit: "NewQbUnit",
    ) -> List[ValidateModelPropertiesError]:
        errors: List[ValidateModelPropertiesError] = []

        if unit.base_unit_scaling_factor is not None and unit.base_unit is None:
            errors.append(
                ValidateModelPropertiesError(
                    f"""
                '{unit.base_unit_scaling_factor}' has been specified, but the following is missing and must be
                        provided: '{unit.base_unit}'.
                        """,
                    "Whole Object",
                )
            )

        if (
            unit.si_base_unit_conversion_multiplier is not None
            and unit.qudt_quantity_kind_uri is None
        ):
            errors.append(
                ValidateModelPropertiesError(
                    f"""
                '{unit.si_base_unit_conversion_multiplier}' has been specified, but the following is missing and must be
                        provided: '{unit.qudt_quantity_kind_uri}'.
                        """,
                    "Whole Object",
                )
            )
        return errors

    optional_attribute_dependencies = pydantic_enforce_optional_attribute_dependencies(
        {
            "base_unit_scaling_factor": ["base_unit"],
            "si_base_unit_conversion_multiplier": ["qudt_quantity_kind_uri"],
        }
    )

    _qudt_quantity_kind_uri_validation = pydantic_validate_uri(
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
