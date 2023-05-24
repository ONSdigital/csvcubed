import pytest

from csvcubed.inspect.inspectorcolumns import (
    AttributeColumn,
    DimensionColumn,
    MeasuresColumn,
    PivotedObservationsColumn,
    StandardShapeObservationsColumn,
    UnitsColumn,
)
from csvcubed.inspect.inspectorcomponents import (
    ExternalAttribute,
    ExternalDimension,
    LocalAttribute,
    LocalDimension,
    LocalMeasure,
    LocalUnit,
)
from csvcubed.inspect.inspectortable import CodeListTable, DataCubeTable, Inspector
from csvcubed.models.cube.cube_shape import CubeShape
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "inspect"


def test_pivoted_shape_inspector_and_tables():
    """
    Tests whether an Inspector correctly represents the expected CSVW structure and
    correctly extracts underlying values from the inspector functions in a pivoted shape
    CSVW input.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-shape"
        / "testing-inspector-pivoted-shape.csv-metadata.json"
    )
    inspector = Inspector(csvw_metadata_json_path)
    tables = inspector.tables

    assert len(tables) == 2
    assert isinstance(tables[0], DataCubeTable)
    assert isinstance(tables[1], CodeListTable)

    assert tables[0].data_set_uri == "testing-inspector-pivoted-shape.csv#dataset"
    assert tables[0].shape == CubeShape.Pivoted
    assert tables[0].csv_url == "testing-inspector-pivoted-shape.csv"
    assert tables[0].title == "Testing Inspector (pivoted shape)"
    assert tables[0].comment == "Inspector test - pivoted shape"
    assert (
        tables[0].description
        == "Testing the Inspector functionality with a pivoted shape cube generated using csvcubed"
    )

    assert tables[1].concept_scheme_uri == "local-dimension-code-list.csv#code-list"
    assert tables[1].csv_url == "local-dimension-code-list.csv"
    assert tables[1].title == "Local dimension code list"
    assert tables[1].comment == "Code list - local dimension"
    assert tables[1].description == "Code list for a locally defined dimension"


def test_pivoted_shape_data_cube_table_columns():
    """
    Tests whether an Inspector correctly represents the expected CSVW structure and
    correctly extracts underlying values from the inspector functions in a standard shape
    CSVW input with locally defined measures and units.
    """
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-shape"
        / "testing-inspector-pivoted-shape.csv-metadata.json"
    )
    inspector = Inspector(csvw_metadata_json_path)
    tables = inspector.tables
    columns = tables[0].columns

    local_dimension_column = columns["LocalDimension"]
    assert local_dimension_column.csv_column_title == "LocalDimension"
    assert (
        local_dimension_column.cell_uri_template
        == "local-dimension-code-list.csv#{+localdimension}"
    )
    assert (
        local_dimension_column.dimension.dimension_uri
        == "testing-inspector-pivoted-shape.csv#dimension/localdimension"
    )
    assert local_dimension_column.dimension.label == "LocalDimension"
    assert local_dimension_column.info.component.property_label == "LocalDimension"
    assert isinstance(local_dimension_column, DimensionColumn)
    assert isinstance(local_dimension_column.dimension, LocalDimension)

    external_dimension_column = columns["ExternalDimension"]
    assert external_dimension_column.csv_column_title == "ExternalDimension"
    assert (
        external_dimension_column.cell_uri_template
        == "http://www.example.org/code-lists/regions/{+externaldimension}"
    )
    assert (
        external_dimension_column.dimension.dimension_uri
        == "http://purl.org/linked-data/sdmx/2009/dimension#refArea"
    )
    assert isinstance(external_dimension_column, DimensionColumn)
    assert isinstance(external_dimension_column.dimension, ExternalDimension)

    local_attribute_column = columns["LocalAttribute"]
    assert local_attribute_column.csv_column_title == "LocalAttribute"
    assert local_attribute_column.cell_uri_template is None
    assert (
        local_attribute_column.attribute.attribute_uri
        == "testing-inspector-pivoted-shape.csv#attribute/localattribute"
    )
    assert local_attribute_column.attribute.label == "LocalAttribute"
    assert isinstance(local_attribute_column, AttributeColumn)
    assert isinstance(local_attribute_column.attribute, LocalAttribute)

    external_attribute_column = columns["ExternalAttribute"]
    assert external_attribute_column.csv_column_title == "ExternalAttribute"
    assert (
        external_attribute_column.cell_uri_template
        == "http://www.example.org/status/{+externalattribute}"
    )
    assert (
        external_attribute_column.attribute.attribute_uri
        == "testing-inspector-pivoted-shape.csv#attribute/externalattribute"
    )
    assert isinstance(external_attribute_column, AttributeColumn)
    assert isinstance(external_attribute_column.attribute, ExternalAttribute)

    pivoted_obs_column = columns["Observations"]
    assert pivoted_obs_column.csv_column_title == "Observations"
    assert pivoted_obs_column.cell_uri_template is None
    assert (
        pivoted_obs_column.unit.unit_uri
        == "testing-inspector-pivoted-shape.csv#unit/some-unit"
    )
    assert pivoted_obs_column.unit.label == "Some Unit"
    assert (
        pivoted_obs_column.measure.measure_uri
        == "testing-inspector-pivoted-shape.csv#measure/some-measure"
    )
    assert pivoted_obs_column.measure.label == "Some Measure"
    assert isinstance(pivoted_obs_column, PivotedObservationsColumn)
    assert isinstance(pivoted_obs_column.unit, LocalUnit)
    assert isinstance(pivoted_obs_column.measure, LocalMeasure)


def test_standard_shape_inspector_locally_defined_measures_units():
    """
    Tests whether an Inspector correctly represents the expected CSVW structure and
    correctly extracts underlying values from the inspector functions in a standard shape
    CSVW input with locally defined measures and units.
    """
    csvw_path = (
        _test_case_base_dir
        / "eurovision"
        / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
    )

    inspector = Inspector(csvw_path)
    inspector_tables = inspector.tables

    dimension_column = inspector_tables[0].columns["Year"]
    assert isinstance(dimension_column, DimensionColumn)
    assert isinstance(dimension_column.dimension, LocalDimension)

    assert dimension_column.csv_column_title == "Year"
    assert dimension_column.cell_uri_template == "year.csv#{+year}"
    assert (
        dimension_column.dimension.dimension_uri
        == "sweden-at-eurovision-complete-dataset.csv#dimension/year"
    )
    assert dimension_column.dimension.label == "Year"

    observation_column = inspector_tables[0].columns["Value"]
    assert isinstance(observation_column, StandardShapeObservationsColumn)
    assert observation_column.csv_column_title == "Value"
    assert observation_column.cell_uri_template == None

    measures_column = inspector_tables[0].columns["Measure"]
    assert isinstance(measures_column, MeasuresColumn)
    assert measures_column.csv_column_title == "Measure"
    assert (
        measures_column.cell_uri_template
        == "sweden-at-eurovision-complete-dataset.csv#measure/{+measure}"
    )

    units_column = inspector_tables[0].columns["Unit"]
    assert isinstance(units_column, UnitsColumn)
    assert units_column.csv_column_title == "Unit"
    assert (
        units_column.cell_uri_template
        == "sweden-at-eurovision-complete-dataset.csv#unit/{+unit}"
    )

    attribute_column = inspector_tables[0].columns["Marker"]
    assert isinstance(attribute_column, AttributeColumn)
    assert attribute_column.csv_column_title == "Marker"
    assert (
        attribute_column.cell_uri_template
        == "sweden-at-eurovision-complete-dataset.csv#attribute/observation-status/{+marker}"
    )
    assert isinstance(attribute_column.attribute, LocalAttribute)
    assert (
        attribute_column.attribute.attribute_uri
        == "sweden-at-eurovision-complete-dataset.csv#attribute/observation-status"
    )
    assert attribute_column.attribute.label == "Observation Status"


def test_standard_shape_inspector_external_measures_units():
    """
    Tests whether an Inspector correctly represents the expected CSVW structure and
    correctly extracts underlying values from the inspector functions in a standard shape
    CSVW input with externally defined measures and units.
    NOTE this test currently does not test anything that isn't covered by the previous test.
    The external measures and units will be tested when the MeasureColumn and UnitColumn classes
    have been fully implemented.
    """
    csvw_path = _test_case_base_dir / "anxiety" / "anxiety.csv-metadata.json"

    inspector = Inspector(csvw_path)
    inspector_tables = inspector.tables

    dimension_column = inspector_tables[0].columns["AREACD"]
    assert isinstance(dimension_column, DimensionColumn)
    assert dimension_column.csv_column_title == "AREACD"
    assert dimension_column.cell_uri_template == "statistical-geography.csv#{+areacd}"
    assert isinstance(dimension_column.dimension, LocalDimension)
    assert (
        dimension_column.dimension.dimension_uri
        == "anxiety.csv#dimension/statistical-geography"
    )
    assert dimension_column.dimension.label == "Statistical Geography"

    observation_column = inspector_tables[0].columns["Value"]
    assert isinstance(observation_column, StandardShapeObservationsColumn)
    assert observation_column.csv_column_title == "Value"
    assert observation_column.cell_uri_template == None

    measures_column = inspector_tables[0].columns["Measure"]
    assert isinstance(measures_column, MeasuresColumn)
    assert measures_column.csv_column_title == "Measure"
    assert (
        measures_column.cell_uri_template
        == "http://example.org/code-lists/example-measure/{+measure}"
    )

    units_column = inspector_tables[0].columns["Unit"]
    assert isinstance(units_column, UnitsColumn)
    assert units_column.csv_column_title == "Unit"
    assert (
        units_column.cell_uri_template
        == "http://example.org/code-lists/example-units/{+unit}"
    )

    attribute_column = inspector_tables[0].columns["Observation Status"]
    assert isinstance(attribute_column, AttributeColumn)
    assert attribute_column.csv_column_title == "Observation Status"
    assert (
        attribute_column.cell_uri_template
        == "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#{+observation_status}"
    )
    assert isinstance(attribute_column.attribute, LocalAttribute)
    assert (
        attribute_column.attribute.attribute_uri
        == "anxiety.csv#attribute/observation-status"
    )
    assert attribute_column.attribute.label == "Observation Status"


if __name__ == "__main__":
    pytest.main()
