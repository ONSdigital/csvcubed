from dataclasses import dataclass


@dataclass
class VirtualConfigurations:
    """
    "Virtual Configurations" are a selection of dictionaries representing
    specific configuration use cases for use and reuse while testing.
    """

    # Dev note:
    # It's counter intuitive but if you put a docstring AFTER the
    # constant then said doctring will be shown against the constant
    # where its in use (i.e when working on tests you can mouseover
    # to see the input without following the code back to here).

    LABEL_ONLY = {
        "label": "A component with just a label",
    }
    """
    A minimal configuration consisting of just a lable field.

    {
        "label": "A component with just a label",
    }
    """

    DIMENSION_CONFIG_POPULATED = {
        "type": "dimension",
        "label": "The New Dimension",
        "description": "A description of the dimension",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "definition_uri": "http://wikipedia.com/#periods",
    }
    """
    A fairly commonplace populated dimension config.

    {
        "type": "dimension",
        "label": "The New Dimension",
        "description": "A description of the dimension",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "definition_uri": "http://wikipedia.com/#periods"
    }
    """

    DIMENSION_WITH_LABEL = {
        "type": "dimension",
        "label": "The New Dimension",
    }
    """
    The minimum configuration for a dimension.

    {
        "type": "dimension",
        "label": "The New Dimension",
    }
    """

    DIMENSION_EXISTING = {
        "type": "dimension",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "cell_uri_template": "http://example.org/code-list/{+some_column}",
    }
    """
    Some minimum configuration to define an existing dimension.
    {
        "type": "dimension",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "cell_uri_template": "http://example.org/code-list/{+some_column}",
    }
    """

    DIMENSION_EXISTING_CODELIST = {
        "label": "The New Dimension",
        "code_list": "http://example.com/code-list#scheme",
        "cell_uri_template": "http://example.com/code-list#{+new_dimension}",
    }
    """
    Configuration for defining a new dimension with an existing codelist.

    {
        "label": "The New Dimension",
        "code_list": "http://example.com/code-list#scheme",
        "cell_uri_template": "http://example.com/code-list#{+new_dimension}",
    }
    """

    ATTRIBUTE_NEW_RESOURCE = {
        "type": "attribute",
        "label": "The New Attribute",
        "description": "A description of the attribute",
        "values": True,
        "required": True,
        "from_existing": "http://gss-cogs/dimesions/#period",
        "definition_uri": "http://wikipedia.com/#periods",
    }
    """
    A configuration for defining a new attribute resource

    {
        "type": "attribute",
        "label": "The New Attribute",
        "description": "A description of the attribute",
        "values": True,
        "required": True,
        "from_existing": "http://gss-cogs/dimesions/#period",
        "definition_uri": "http://wikipedia.com/#periods",
    }
    """

    ATTRIBUTE_NEW_LITERAL = {
        "type": "attribute",
        "label": "I'm an attribute",
        "data_type": "int",
    }
    """
    A configuration for defining a new attribute literal.

    {
        "type": "attribute",
        "label": "I'm an attribute",
        "data_type": "int",
    }
    """

    ATTRIBUTE_NEW_LITERAL_NO_LABEL = {
        "type": "attribute",
        "data_type": "int",
    }
    """
    A configuration for defining a new attribute literal.

    {
        "type": "attribute",
        "label": "I'm an attribute",
        "data_type": "int",
    }
    """

    ATTRIBUTE_NEW_RESOURCE_WITH_VALUES = {
        "type": "attribute",
        "label": "Attribute Label",
        "description": "A description of the attribute",
        "values": [
            {
                "label": "Value Label A",
                "description": "Value Description A",
                "from_existing": "http://example.org/sources/A",
                "definition_uri": "http://example.org/definitions/A",
            },
            {
                "label": "Value Label B",
                "description": "Value Description B",
                "from_existing": "http://example.org/sources/B",
                "definition_uri": "http://example.org/definitions/B/",
            },
        ],
    }
    """
    A new attribute resource configuration with values defined.

    {
        "type": "attribute",
        "label": "Attribute Label",
        "description": "A description of the attribute",
        "values": [
            {
                "label": "Value Label A",
                "description": "Value Description A",
                "from_existing": "http://example.org/sources/A",
                "definition_uri": "http://example.org/definitions/A",
            },
            {
                "label": "Value Label B",
                "description": "Value Description B",
                "from_existing": "http://example.org/sources/B",
                "definition_uri": "http://example.org/definitions/B/",
            },
        ],
    }
    """

    ATTRIBUTE_EXISTING_RESOURCE = {
        "type": "attribute",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "required": False,
    }
    """
    Configuration for an attribute resource from existing.

    {
        "type": "attribute",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "required": False
    }
    """

    ATTRIBUTE_EXISTING_LITERAL = {
        "type": "attribute",
        "data_type": "string",
        "from_existing": "http://gss-cogs/dimesions/#period",
    }
    """
    Configuration for an attribute literal from existing.

    {
        "type": "attribute",
        "data_type": "string",
        "from_existing": "http://gss-cogs/dimesions/#period",
    }
    """

    MEASURE_NEW = {"type": "measures", "values": True}
    """
    Configuration for a new measure

    {"type": "measures", "values": True}
    """

    MEASURE_EXISTING = {
        "type": "measures",
        "cell_uri_template": "http://example.org/measures/{+existing_measure}",
    }
    """
    Configuration for an existing measure.

    {
        "type": "measures",
        "cell_uri_template": "http://example.org/measures/{+existing_measure}",
    }
    """

    UNIT_NEW = {"type": "units", "values": True}
    """
    Configuration for a new unit

    {"type": "units", "values": True}
    """

    UNIT_EXISTING = {
        "type": "units",
        "cell_uri_template": "http://example.org/unit/{+existing_unit}",
    }
    """
    Configuration for an existing unit

    {
        "type": "units",
        "cell_uri_template": "http://example.org/unit/{+existing_unit}",
    }
    """
