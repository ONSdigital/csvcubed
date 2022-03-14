"""
Cube Components
---------------

Utilities to help when handling qube components data.
"""

from enum import Enum
from pathlib import Path
import os


class ComponentPropertyAttributeURI(Enum):
    """
    The uris of component attributes.
    """
    UnitMeasure = "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"

    MeasureType = "http://purl.org/linked-data/cube#measureType"


class ComponentPropertyTypeURI(Enum):
    """
    The type uris of component properties.
    """

    Dimension = "http://purl.org/linked-data/cube#DimensionProperty"
    """ The component is of type qb:Diemension. """

    Attribute = "http://purl.org/linked-data/cube#AttributeProperty"
    """ The component is of type qb:Attribute. """

    Measure = "http://purl.org/linked-data/cube#MeasureProperty"
    """ The component is of type qb:Measure. """


class ComponentPropertyType(Enum):
    """
    The type of component properties.
    """

    Dimension = "Dimension"
    """ The component is of type qb:Diemension. """

    Attribute = "Attribute"
    """ The component is of type qb:Attribute. """

    Measure = "Measure"
    """ The component is of type qb:Measure. """


def get_printable_component_property_type(property_type: str) -> str:
    """
    Produces the user-friendly name of component property type.

    Member of :file:`./utils/qb/components.py`

    :return: `str` - user-friendly name of component property type.
    """
    if ComponentPropertyTypeURI.Dimension.value == property_type:
        return ComponentPropertyType.Dimension.value
    elif ComponentPropertyTypeURI.Attribute.value == property_type:
        return ComponentPropertyType.Attribute.value
    elif ComponentPropertyTypeURI.Measure.value == property_type:
        return ComponentPropertyType.Measure.value
    else:
        raise Exception(f"Property type {property_type} is not supported.")


def get_printable_component_property(
    input_file_path: Path, component_property: str
) -> str:
    """
    Produces the user-friendly property of the component property.

    Member of :file:`./utils/qb/components.py`

    :return: `str` - url or relative path
    """
    if not component_property.startswith("file://"):
        return component_property

    component_property = component_property.removeprefix("file://")
    try:
        relative_path: str = os.path.relpath(
            component_property,
            input_file_path.parent,
        )
        return relative_path
    except Exception:
        return component_property
