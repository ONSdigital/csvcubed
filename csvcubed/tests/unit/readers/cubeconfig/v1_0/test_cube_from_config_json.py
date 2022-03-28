import os
import pytest
from csvcubed.cli.build import build as cli_build
from csvcubed.readers.cubeconfig.schema_versions import QubeConfigJsonSchemaVersion
from csvcubed.readers.cubeconfig.v1_0.configdeserialiser import *
from csvcubed.readers.cubeconfig.v1_0.configdeserialiser import _get_qb_column_from_json
from tests.unit.test_baseunit import get_test_cases_dir
from definitions import ROOT_DIR_PATH

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"
SCHEMA_PATH_FILE = Path(ROOT_DIR_PATH, "csvcubed", "schema", "cube-config-schema.json")


def test_build():

    config = Path(TEST_CASE_DIR, "cube_data_config_ok.json")
    output = Path("./out")
    csv = Path(TEST_CASE_DIR, "cube_data_config_ok.csv")
    cli_build(
        config_path=config,
        output_directory=output,
        csv_path=csv,
        fail_when_validation_error_occurs=True,
        validation_errors_file_out=Path("validation_errors.json"),
    )


def _check_new_attribute_column(
    column: QbColumn, column_config: dict, column_data: list, title: str
) -> None:

    assert isinstance(column, QbColumn)
    assert isinstance(column.structural_definition, NewQbAttribute)
    assert hasattr(column, "type") is False
    assert column.csv_column_title == title
    assert column.uri_safe_identifier == uri_safe(title)
    assert column.uri_safe_identifier_override == column_config.get(
        "uri_safe_identifier_override"
    )

    sd = column.structural_definition
    assert sd.label == column_config.get("label", title)
    assert sd.description == column_config.get("description")
    assert sd.is_required == column_config.get("required", False)
    assert sd.parent_attribute_uri == column_config.get("from_existing")
    assert sd.source_uri == column_config.get("definition_uri")
    assert isinstance(sd.arbitrary_rdf, list)
    assert isinstance(sd.new_attribute_values, list)
    for av in sd.new_attribute_values:
        assert isinstance(av, NewQbAttributeValue)
        assert hasattr(av, "label")
        if isinstance(column_config["values"], bool):
            assert av.label in column_data
        else:
            assert av.label in [v["label"] for v in column_config["values"]]


def _check_new_dimension_column(
    column: QbColumn, column_config: dict, column_data: list, title: str
) -> None:
    assert isinstance(column, QbColumn)
    assert isinstance(column.structural_definition, NewQbDimension)

    # Check code_list default constructions (from data)
    assert isinstance(column.structural_definition.code_list, NewQbCodeList)
    assert isinstance(column.structural_definition.code_list.metadata, CatalogMetadata)
    assert hasattr(column, "type") is False
    assert column.structural_definition.label == column_config.get("label", title)
    assert column.structural_definition.description == column_config.get("description")
    assert column.structural_definition.parent_dimension_uri == column_config.get(
        "from_existing"
    )
    assert column.structural_definition.source_uri == column_config.get(
        "definition_uri"
    )

    assert isinstance(column.structural_definition.code_list.concepts, list)
    assert isinstance(column.structural_definition.code_list.concepts[0], NewQbConcept)
    assert column.csv_column_uri_template == column_config.get("cell_uri_template")

    unique_column_data = list(sorted(set(column_data)))
    assert len(column.structural_definition.code_list.concepts) == len(
        unique_column_data
    )
    for concept in column.structural_definition.code_list.concepts:
        assert concept.label in unique_column_data
        assert concept.code in unique_column_data
        assert concept.description is None
        assert concept.parent_code is None
        assert concept.sort_order is None
        assert concept.uri_safe_identifier == uri_safe(concept.label)
        assert concept.uri_safe_identifier_override is None


def test_01_build_config_ok():
    """
    Valid Cube from Data using Convention (no config json)
    """
    test_data_path = Path(
        os.path.join(TEST_CASE_DIR, "cube_data_config_ok.csv")
    ).resolve()
    test_json_path = Path(
        os.path.join(TEST_CASE_DIR, "cube_data_config_ok.json")
    ).resolve()
    print(f"test_case_data: {test_data_path}")
    cube, validation_errors = cli_build(
        config_path=test_json_path,
        csv_path=test_data_path,
        output_directory=Path("./out"),
        fail_when_validation_error_occurs=True,
        validation_errors_file_out=Path("validation_errors.json"),
    )
    assert isinstance(cube, Cube)
    assert isinstance(validation_errors, List)
    assert isinstance(cube.columns, list)
    for column in cube.columns:
        assert isinstance(column, QbColumn)

    col_dim_0 = cube.columns[0]
    assert isinstance(col_dim_0.structural_definition, NewQbDimension)
    assert isinstance(col_dim_0.structural_definition.code_list, NewQbCodeList)
    assert isinstance(
        col_dim_0.structural_definition.code_list.metadata, CatalogMetadata
    )
    assert isinstance(col_dim_0.structural_definition.code_list.concepts, list)
    assert isinstance(
        col_dim_0.structural_definition.code_list.concepts[0], NewQbConcept
    )

    col_dim_1 = cube.columns[1]
    assert isinstance(col_dim_1.structural_definition, NewQbDimension)
    assert isinstance(
        col_dim_1.structural_definition.code_list.metadata, CatalogMetadata
    )
    assert isinstance(col_dim_1.structural_definition.code_list.concepts, list)
    assert isinstance(
        col_dim_1.structural_definition.code_list.concepts[0], NewQbConcept
    )

    col_dim_2 = cube.columns[2]
    assert isinstance(col_dim_2.structural_definition, NewQbDimension)
    assert isinstance(
        col_dim_2.structural_definition.code_list.metadata, CatalogMetadata
    )
    assert isinstance(col_dim_2.structural_definition.code_list.concepts, list)
    assert isinstance(
        col_dim_2.structural_definition.code_list.concepts[0], NewQbConcept
    )

    col_attr_1 = cube.columns[3]
    assert isinstance(col_attr_1.structural_definition, NewQbAttribute)
    assert isinstance(col_attr_1.structural_definition.new_attribute_values, list)
    assert isinstance(
        col_attr_1.structural_definition.new_attribute_values[0], NewQbAttributeValue
    )

    col_observation = cube.columns[4]
    assert isinstance(
        col_observation.structural_definition, QbMultiMeasureObservationValue
    )
    assert col_observation.structural_definition.unit is None
    assert col_observation.structural_definition.data_type == "decimal"

    col_measure = cube.columns[5]
    assert isinstance(col_measure.structural_definition, QbMultiMeasureDimension)
    assert isinstance(col_measure.structural_definition.measures, list)
    assert isinstance(col_measure.structural_definition.measures[0], NewQbMeasure)

    col_unit = cube.columns[6]
    assert isinstance(col_unit.structural_definition, QbMultiUnits)
    assert isinstance(col_unit.structural_definition.units, list)
    assert isinstance(col_unit.structural_definition.units[0], NewQbUnit)


def test_02_00_dimension_new_no_type():
    """
    Checks a New dimension is created when omitting 'type'
    """
    column_data = ["a", "b", "c", "a"]
    dimension_config = {
        "label": "The New Dimension",
    }
    data = pd.Series(column_data, name="Dimension Heading")

    column = map_column_to_qb_component("New Dimension", dimension_config, data)
    _check_new_dimension_column(column, dimension_config, column_data, "New Dimension")


def test_02_01_dimension_new_ok():
    """
    Populates all options and confirms the New Dimension & CodeList classes are created
    and all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    dimension_config = {
        "type": "dimension",
        "label": "The New Dimension",
        "description": "A description of the dimension",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "definition_uri": "http://wikipedia.com/#periods",
        # 'code_list': '', -> defaults to True so should be a NewQbCodeList
    }
    data = pd.Series(column_data, name="Dimension Heading")

    column = map_column_to_qb_component("New Dimension", dimension_config, data)
    _check_new_dimension_column(column, dimension_config, column_data, "New Dimension")


def test_02_03_dimension_new_ok():
    """
    Check New dimension when omitting description, from_existing, definition_url and
    cell_uri_template
    """
    column_data = ["a", "b", "c", "a"]
    dimension_config = {
        "type": "dimension",
        "label": "The New Dimension",
    }
    data = pd.Series(column_data, name="Dimension Heading")

    column = map_column_to_qb_component("New Dimension", dimension_config, data)
    _check_new_dimension_column(column, dimension_config, column_data, "New Dimension")


def test_03_dimension_existing_ok():
    """
    Populates options for an Existing Dimension & New CodeList classes are created
    and all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    dimension_config = {
        "type": "dimension",
        "from_existing": "http://gss-cogs/dimesions/#period",
        "cell_uri_template": "http://example.org/code-list/{+some_column}",
    }
    data = pd.Series(column_data, name="Dimension Heading")

    column = map_column_to_qb_component("New Dimension", dimension_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    assert hasattr(column, "type") is False

    # And the Column is of the expected type
    assert isinstance(column.structural_definition, ExistingQbDimension)
    assert not hasattr(column.structural_definition, "code_list")
    assert (
        column.structural_definition.dimension_uri == dimension_config["from_existing"]
    )
    assert column.structural_definition.range_uri is None
    assert isinstance(column.structural_definition.arbitrary_rdf, list)
    assert column.structural_definition.arbitrary_rdf == []


def test_04_01_attribute_new_ok():
    """
    Populates all options and confirms the New Attribute and checks all properties are mapped
    through correctly
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {
        "type": "attribute",
        "label": "The New Attribute",
        "description": "A description of the attribute",
        "values": True,
        "required": True,
        "from_existing": "http://gss-cogs/dimesions/#period",
        "definition_uri": "http://wikipedia.com/#periods",
    }
    data = pd.Series(column_data, name="Attribute Heading")

    column = map_column_to_qb_component("New Attribute", column_config, data)
    _check_new_attribute_column(column, column_config, column_data, "New Attribute")


def test_04_03_attribute_new_ok():
    """
    Checks New attribute when description, values, from_existing and definition_uri options
    are omitted
    ** Values False
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {
        "type": "attribute",
        "label": "Attribute Label",
        "description": "A description of the attribute",
        "values": False,
    }
    data = pd.Series(column_data, name="Attribute Heading")

    column = map_column_to_qb_component("New Attribute", column_config, data)
    _check_new_attribute_column(column, column_config, column_data, "New Attribute")


def test_04_04_attribute_new_ok():
    """
    Checks New attribute when description, values, from_existing and definition_uri options
    are omitted
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {
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
    data = pd.Series(column_data, name="Attribute Heading")

    column = map_column_to_qb_component("New Attribute", column_config, data)
    _check_new_attribute_column(column, column_config, column_data, "New Attribute")


def test_05_01_attribute_existing_ok():
    """
    Populates options for an Existing Attribute checks all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {
        "type": "attribute",
        "from_existing": "http://gss-cogs/dimesions/#period",
    }
    data = pd.Series(column_data, name="Attribute Heading")

    column = map_column_to_qb_component("Existing Attribute", column_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    assert hasattr(column, "type") is False

    # And the Column is of the expected type
    assert isinstance(column.structural_definition, ExistingQbAttribute)
    assert not hasattr(column.structural_definition, "code_list")
    assert column.structural_definition.attribute_uri == column_config["from_existing"]
    assert isinstance(column.structural_definition.arbitrary_rdf, list)
    assert column.structural_definition.arbitrary_rdf == []


def test_05_02_attribute_existing_ok():
    """
    Checks that new (non nul) values are created from data for an existing attribute
    ** values: True
    """
    column_data = ["a", "b", None, "a"]
    column_config = {
        "type": "attribute",
        "from_existing": "http://gss-cofs.github.io/attributes/trade-direction",
        "required": False,
        "values": True,
    }
    data = pd.Series(column_data, name="Attribute Heading")

    column = map_column_to_qb_component("Existing Attribute", column_config, data)

    assert isinstance(column, QbColumn)
    assert hasattr(column, "type") is False

    sd = column.structural_definition
    assert isinstance(sd, ExistingQbAttribute)
    assert not hasattr(sd, "code_list")
    # assert sd.definition_uri == column_config.get('from_existing')
    assert sd.attribute_uri == column_config.get("from_existing", "")
    assert sd.is_required == column_config.get("required")
    assert isinstance(sd.arbitrary_rdf, list)
    assert sd.arbitrary_rdf == []
    if column_config.get("required") is True:
        data_vals = set(column_data)
    else:
        data_vals = set([v for v in column_data if v])
    assert len(sd.new_attribute_values) == len(list(data_vals))
    for value in sd.new_attribute_values:
        assert hasattr(value, "label")
        assert value.label in data_vals


def test_05_03_attribute_existing_broke():
    """
    Checks that Values =  False, which is not a supported value, behaves as expected
    """
    column_data = ["a", "b", None, "a"]
    column_config = {
        "type": "attribute",
        "from_existing": "http://gss-cofs.github.io/attributes/trade-direction",
        "required": False,
        "values": False,
    }
    data = pd.Series(column_data, name="Attribute Heading")

    with pytest.raises(ValueError) as err:
        column = map_column_to_qb_component("Existing Attribute", column_config, data)
    assert err.value.args[0] == "Unexpected value for 'newAttributeValues': False"


def test_06_measure_new_ok():
    """
    Populates options for an New Measures checks all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {"type": "measures", "values": True}
    data = pd.Series(column_data, name="New Measure")

    column = map_column_to_qb_component("New Measure", column_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    # And the Column is of the expected type
    assert hasattr(column, "type") is False
    assert column.csv_column_title == "New Measure"
    assert column.uri_safe_identifier == uri_safe("New Measure")
    assert column.uri_safe_identifier_override == None

    sd = column.structural_definition
    assert isinstance(sd, QbMultiMeasureDimension)
    assert isinstance(sd.measures, list)
    assert len(sd.measures) == len(set(data))
    for measure in sd.measures:
        assert isinstance(measure, NewQbMeasure)
        assert measure.label in column_data


def test_07_measure_existing_ok():
    """
    Populates options for existing Measures checks all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {
        "type": "measures",
        "cell_uri_template": "http://example.org/measures/{+existing_measure}",
    }
    data = pd.Series(column_data, name="Existing Measure Series")

    column = map_column_to_qb_component("Existing Measure", column_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    assert hasattr(column, "type") is False
    assert column.uri_safe_identifier == uri_safe("Existing Measure")
    assert column.uri_safe_identifier_override is None

    sd = column.structural_definition
    assert isinstance(sd, QbMultiMeasureDimension)
    assert isinstance(sd.measures, list)
    assert len(sd.measures) == len(set(data))
    for measure in sd.measures:
        assert isinstance(measure, ExistingQbMeasure)
        assert measure.measure_uri.startswith(
            column_config["cell_uri_template"][
                : column_config["cell_uri_template"].find("{")
            ]
        )
        assert (
            measure.measure_uri[column_config["cell_uri_template"].find("{") :]
            in column_data
        )


def test_08_unit_new_ok():
    """
    Populates options for an New Units checks all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {"type": "units", "values": True}
    data = pd.Series(column_data, name="New Units")

    column = map_column_to_qb_component("New Units", column_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    # And the Column is of the expected type
    assert hasattr(column, "type") is False
    assert column.csv_column_title == "New Units"
    assert column.uri_safe_identifier == uri_safe("New Units")
    assert column.uri_safe_identifier_override == None

    sd = column.structural_definition
    assert isinstance(sd, QbMultiUnits)
    assert isinstance(sd.units, list)
    assert len(sd.units) == len(set(data))
    for unit in sd.units:
        assert isinstance(unit, NewQbUnit)
        assert unit.label in column_data


def test_09_units_existing_ok():
    """
    Populates options for an Existing Units checks all properties are mapped through correctly
    """
    column_data = ["a", "b", "c", "a"]
    column_config = {
        "type": "units",
        "cell_uri_template": "http://example.org/unit/{+existing_unit}",
    }
    data = pd.Series(column_data, name="Existing Unit Series")

    column = map_column_to_qb_component("Existing Unit", column_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    assert hasattr(column, "type") is False
    assert column.uri_safe_identifier == uri_safe("Existing Unit")
    assert column.uri_safe_identifier_override is None

    sd = column.structural_definition
    assert isinstance(sd, QbMultiUnits)
    assert isinstance(sd.units, list)
    assert len(sd.units) == len(set(data))
    for unit in sd.units:
        assert isinstance(unit, ExistingQbUnit)
        assert unit.unit_uri.startswith(
            column_config["cell_uri_template"][
                : column_config["cell_uri_template"].find("{")
            ]
        )
        assert (
            unit.unit_uri[column_config["cell_uri_template"].find("{") :] in column_data
        )


def test_10_observation_ok():
    column_data = ["a", "b", "c", "a"]
    column_config = {
        "type": "observations",
        "data_type": "decimal",
        # 'unit': None,
        # 'measure': None
    }
    # "properties": {
    #     "type": {
    #         "description": "Column type.",
    #         "type": "string",
    #         "default": "observation"
    #     },
    #     "data_type": {
    #         "$ref": "#/definitions/v1.0/dataTypes"
    #     },
    #     "unit": {
    #         "description": "The units being measured in this observation",
    #         "$ref": "#/definitions/v1.0/valueTypes/unitType"
    #     },
    #     "measure": {
    #         "description": "The measure used for this observation",
    #         "$ref": "#/definitions/v1.0/valueTypes/measureType"
    #     }
    data = pd.Series(column_data, name="Observation Series")

    column = map_column_to_qb_component("Observations", column_config, data)

    # Confirm a Column is returned
    assert isinstance(column, QbColumn)
    assert hasattr(column, "type") is False
    assert column.uri_safe_identifier == uri_safe("observations")
    assert column.uri_safe_identifier_override is None

    sd = column.structural_definition
    assert isinstance(sd, QbMultiMeasureObservationValue)
    assert sd.unit is None
    assert sd.data_type == "decimal"


def test_new_dimension_existing_code_list():
    """
    Ensure we can correctly define a new dimension using an existing code-list
    """
    column_data = ["a", "b", "c", "a"]
    dimension_config = {
        "label": "The New Dimension",
        "code_list": "http://example.com/code-list#scheme",
        "cell_uri_template": "http://example.com/code-list#{+new_dimension}",
    }
    data = pd.Series(column_data, name="Dimension Heading")

    column = map_column_to_qb_component("New Dimension", dimension_config, data)

    assert isinstance(column.structural_definition, NewQbDimension)
    dimension = column.structural_definition
    assert dimension.label == "The New Dimension"
    assert isinstance(dimension.code_list, ExistingQbCodeList)
    assert (
        dimension.code_list.concept_scheme_uri == "http://example.com/code-list#scheme"
    )
    assert (
        column.csv_column_uri_template
        == "http://example.com/code-list#{+new_dimension}"
    )


def test_column_template_expansion():
    """
    Test that when using a column template, we see the default parameters expanded as expected.
    """
    data = pd.DataFrame({"The Column": ["a", "b", "c", "a"]})

    column = _get_qb_column_from_json(
        {
            "from_template": "year",
        },
        "The Column",
        data,
        QubeConfigJsonSchemaVersion.V1_0.value,
    )

    assert isinstance(column.structural_definition, NewQbDimension)
    dimension = column.structural_definition
    assert dimension.label == "Year"


if __name__ == "__main__":
    pytest.main()
