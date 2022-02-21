"""
Cube Components
---------------

Utilities to help when handling qube components data.
"""

from enum import Enum
from pathlib import Path


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


def get_printable_component_property(component_property: str, csvw_path: Path) -> str:
    """
    Produces the user-friendly property of the component property.
    More specifically, if the property is a url, the url should be the printable.
    If the property is a file, the relative file path should be the printable.

    Member of :file:`./utils/qb/components.py`

    :return: `str` - url or relative path
    """

    if component_property.startswith("file://") == False:
        return component_property

    component_property_printable = str(csvw_path).removesuffix(
        "/" + csvw_path.name
    ) + component_property.removeprefix("file://" + str(Path.cwd()))

    return component_property_printable
