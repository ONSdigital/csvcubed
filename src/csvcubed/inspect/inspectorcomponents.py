"""
Inspector Components
--------------------

Class definitions for the different component types that may be accessed
within an inspector column.
"""

from dataclasses import dataclass, field

from csvcubed.inspect.lazyfuncdescriptor import lazy_func_field
from csvcubed.models.inspect.sparqlresults import QubeComponentResult


@dataclass(frozen=True)
class Dimension:
    """
    Represents a dimension component. It allows access to the dimension's URI.
    Inherited by the implementations of externally and locally defined dimensions.
    """

    dimension_component: QubeComponentResult = field(repr=False)

    def _get_dimension_uri(self) -> str:
        return self.dimension_component.property

    dimension_uri: str = lazy_func_field(_get_dimension_uri)


@dataclass(frozen=True)
class ExternalDimension(Dimension):
    """A dimension defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalDimension(Dimension):
    """A dimension which is defined locally in this data set."""

    def _get_label(self):
        dimension_label = self.dimension_component.property_label
        if dimension_label is None:
            raise ValueError("Could not locate label for locally defined dimension")

        return dimension_label

    label: str = lazy_func_field(_get_label)

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class Attribute:
    """
    The base class for an attribute component. Can exist either as a locally defined or
    externally defined attribute.
    """

    attribute_component: QubeComponentResult = field(repr=False)

    def _get_attribute_uri(self) -> str:
        return self.attribute_component.property

    attribute_uri: str = lazy_func_field(_get_attribute_uri)


@dataclass(frozen=True)
class ExternalAttribute(Attribute):
    """An attribute defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalAttribute(Attribute):
    """An attribute which is defined locally in this data set."""

    def _get_label(self):
        attribute_label = self.attribute_component.property_label
        if attribute_label is None:
            raise ValueError("Could not locate label for locally defined dimension")

        return attribute_label

    label: str = lazy_func_field(_get_label)

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class Unit:
    """
    Represents a unit, allowing access to its URI. Goes on to be inherited by the
    externally and locally defined unit classes.
    """

    unit_uri: str


@dataclass(frozen=True)
class ExternalUnit(Unit):
    """A unit defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalUnit(Unit):
    """A unit which is defined locally in this data set."""

    label: str

    # todo: Should bring parent/subPropertyOf value in here.


@dataclass(frozen=True)
class Measure:
    """
    Represents a measure, allowing access to its URI. Inherited by the
    externally and locally defined measure class implementations.
    """

    measure_uri: str


@dataclass(frozen=True)
class ExternalMeasure(Measure):
    """A measure defined externally to this data set."""

    pass


@dataclass(frozen=True)
class LocalMeasure(Measure):
    """A measure which is defined locally in this data set."""

    label: str

    # todo: Should bring parent/subPropertyOf value in here.
