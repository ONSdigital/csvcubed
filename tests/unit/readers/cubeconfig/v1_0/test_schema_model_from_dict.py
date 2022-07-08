import csvcubed.readers.cubeconfig.v1.columnschema as schema
from csvcubed.readers.cubeconfig.v1.mapcolumntocomponent import _from_column_dict_to_schema_model

from .virtualconfigs import VirtualConfigurations as vc

def test_attribute_new_literal():
    """
    Test that when given an appropriate input, we can correctly identify
    a new attribute literal from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("New Attribute Literal", vc.ATTRIBUTE_NEW_LITERAL)
    assert isinstance(schema_mapping, schema.NewAttributeLiteral)


def test_attribute_new_resource():
    """
    Test that when given an appropriate input, we can correctly identify
    a new attribute resource from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("New Attribute Resource", vc.ATTRIBUTE_NEW_RESOURCE)
    assert isinstance(schema_mapping, schema.NewAttributeResource)


def test_attribute_existing_literal():
    """
    Test that when given an appropriate input, we can correctly identify
    an existing attribute literal from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("Existing Attribute Literal", vc.ATTRIBUTE_EXISTING_LITERAL)
    assert isinstance(schema_mapping, schema.ExistingAttributeLiteral)


def test_attribute_existing_resource():
    """
    Test that when given an appropriate input, we can correctly identify
    an existing attribute resource from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("Existing Attribute Resource", vc.ATTRIBUTE_EXISTING_RESOURCE)
    assert isinstance(schema_mapping, schema.ExistingAttributeResource)


def test_dimension_new():
    """
    Test that when given an appropriate input, we can correctly identify
    a new dimension from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("New Dimension", vc.DIMENSION_WITH_LABEL)
    assert isinstance(schema_mapping, schema.NewDimension)


def test_dimension_existing():
    """
    Test that when given an appropriate input, we can correctly identify
    an existing dimension from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("Existing Dimension", vc.DIMENSION_EXISTING)
    assert isinstance(schema_mapping, schema.ExistingDimension)


def test_measure_new():
    """
    Test that when given an appropriate input, we can correctly identify
    a new measure from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("New Measure", vc.MEASURE_NEW)
    assert isinstance(schema_mapping, schema.NewMeasures)


def test_measure_existing():
    """
    Test that when given an appropriate input, we can correctly identify
    an existing measure from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("Existing Measure", vc.MEASURE_EXISTING)
    assert isinstance(schema_mapping, schema.ExistingMeasures)


def test_unit_new():
    """
    Test that when given an appropriate input, we can correctly identify
    a new unit from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("New Unit", vc.UNIT_NEW)
    assert isinstance(schema_mapping, schema.NewUnits)


def test_unit_existing():
    """
    Test that when given an appropriate input, we can correctly identify
    an existing unit from its schema model.
    """
    schema_mapping = _from_column_dict_to_schema_model("Existing Unit", vc.UNIT_EXISTING)
    assert isinstance(schema_mapping, schema.ExistingUnits)



