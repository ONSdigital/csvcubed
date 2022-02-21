import pytest

from csvcubed.utils.qb.components import (
    ComponentPropertyType,
    get_printable_component_property_type,
)


def test_printable_component_property_type_dimension():
    """
    Should return "Dimension" when the input is http://purl.org/linked-data/cube#DimensionProperty
    """
    property_type = get_printable_component_property_type(
        "http://purl.org/linked-data/cube#DimensionProperty"
    )
    assert property_type == ComponentPropertyType.Dimension.value


def test_printable_component_property_type_attribute():
    """
    Should return "Attribute" when the input is http://purl.org/linked-data/cube#AttributeProperty
    """
    property_type = get_printable_component_property_type(
        "http://purl.org/linked-data/cube#AttributeProperty"
    )
    assert property_type == ComponentPropertyType.Attribute.value


def test_printable_component_property_type_measure():
    """
    Should return "Attribute" when the input is http://purl.org/linked-data/cube#MeasureProperty
    """
    property_type = get_printable_component_property_type(
        "http://purl.org/linked-data/cube#MeasureProperty"
    )
    assert property_type == ComponentPropertyType.Measure.value


def test_printable_component_property_type_unsupported_exception():
    """
    Should raise an exception when the property is not supported (i.e. property is not of type Dimension, Attribute or Measure).
    """
    with pytest.raises(Exception):
        get_printable_component_property_type(
            "http://purl.org/linked-data/cube#UnsupportedProperty"
        )
