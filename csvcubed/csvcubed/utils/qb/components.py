"""
Cube Components
---------------

Utilities to help when handling qube components data.
"""

from enum import Enum


class ComponentPropertyType(Enum):
    """
    The type of qube component.
    """

    Dimension = "DimensionProperty"
    """ The component is of type qb:Diemension. """

    Attribute = "AttributeProperty"
    """ The component is of type qb:Attribute. """

    Measure = "MeasureProperty"
    """ The component is of type qb:Measure. """


def get_printable_component_property_type(property_type: str) -> str:
    """
    Produces the user-friendly name of component property type.

    Member of :file:`./utils/qb/components.py`

    :return: `str` - user-friendly name of component property type.
    """
    if ComponentPropertyType.Dimension.value in property_type:
        return ComponentPropertyType.Dimension.value
    elif ComponentPropertyType.Attribute.value in property_type:
        return ComponentPropertyType.Attribute.value
    elif ComponentPropertyType.Measure.value in property_type:
        return ComponentPropertyType.Measure.value
    else:
        raise Exception(f"Property type {property_type} is not supported.")
