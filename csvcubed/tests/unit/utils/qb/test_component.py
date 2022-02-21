from pathlib import Path
import pytest

from csvcubed.utils.qb.components import (
    ComponentPropertyType,
    get_printable_component_property,
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


def test_get_printable_component_property_url():
    """
    If the property is a url, the url should be the printable.
    """
    component_property = get_printable_component_property(
        "http://gss-data.org.uk/def/measure/beer-duty-receipts",
        "csvcubed/cli/inspect/out/alcohol-bulletin.csv-metadata.json",
    )

    assert component_property == "http://gss-data.org.uk/def/measure/beer-duty-receipts"


def test_get_printable_component_property_file():
    """
    If the property is a file, the relative file path should be the printable.
    """
    component_property_printable = get_printable_component_property(
        "file:///workspaces/csvcubed/alcohol-bulletin.csv#dimension/clearance-origin",
        Path("csvcubed/cli/inspect/out/alcohol-bulletin.csv-metadata.json"),
    )

    assert (
        component_property_printable
        == "csvcubed/cli/inspect/out/alcohol-bulletin.csv#dimension/clearance-origin"
    )
