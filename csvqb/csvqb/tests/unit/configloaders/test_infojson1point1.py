import pytest
import pandas as pd

from csvqb.tests.unit.test_baseunit import get_test_cases_dir
from csvqb.configloaders.infojson import get_cube_from_info_json
from csvqb.utils.iterables import first
from csvqb.models.cube import *

info_json_1_1_test_cases_dir = get_test_cases_dir() / "configloaders" / "infojson1-1"


def test_units_loading():
    """
    Test that multi-units columns with existing and new units can be successfully loaded using the new
    info.json v1.1 syntax using all possible configuration types.
    """
    data = pd.read_csv(
        get_test_cases_dir() / "configloaders" / "infojson1-1" / "units.csv"
    )
    cube, json_schema_validation_error = get_cube_from_info_json(
        get_test_cases_dir() / "configloaders" / "infojson1-1" / "units.json",
        data,
    )

    existing_units = _get_column_definition(cube, "Existing Units")
    new_units = _get_column_definition(cube, "New Units")
    new_units_2 = _get_column_definition(cube, "New Units 2")
    new_units_3 = _get_column_definition(cube, "New Units 3")

    assert existing_units is not None
    assert isinstance(existing_units.component, QbMultiUnits)
    assert len(existing_units.component.units) == 1
    unit = existing_units.component.units[0]
    assert isinstance(unit, ExistingQbUnit)
    assert unit.unit_uri == "http://example.com/units/some-existing-unit"
    assert (
        existing_units.csv_column_uri_template
        == "http://example.com/units/{+existing_units}"
    )

    assert new_units is not None
    assert isinstance(new_units.component, QbMultiUnits)
    assert len(new_units.component.units) == 1
    unit = new_units.component.units[0]
    assert isinstance(unit, NewQbUnit)
    assert unit.label == "New Unit 1"
    assert new_units.csv_column_uri_template is None

    assert new_units_2 is not None
    assert isinstance(new_units_2.component, QbMultiUnits)
    assert len(new_units_2.component.units) == 1
    unit = new_units_2.component.units[0]
    assert isinstance(unit, NewQbUnit)
    assert unit.label == "New Unit 2"
    assert unit.uri_safe_identifier_override == "newunit-2"
    assert unit.description == "New Unit 2 Comment"
    assert unit.source_uri == "http://example.com/units/defs/new-unit-2"
    assert isinstance(unit.base_unit, ExistingQbUnit)
    assert (
        unit.base_unit.unit_uri
        == "http://gss-data.org.uk/def/concept/measurement-units/some-unit"
    )
    assert unit.base_unit_scaling_factor == 7
    assert (
        unit.qudt_quantity_kind_uri
        == "http://qudt.org/vocab/quantitykind/AbsoluteHumidity"
    )
    assert unit.si_base_unit_conversion_multiplier == 200
    assert new_units_2.csv_column_uri_template is None

    assert new_units_3 is not None
    assert isinstance(new_units_3.component, QbMultiUnits)
    assert len(new_units_3.component.units) == 1
    unit = new_units_3.component.units[0]
    assert isinstance(unit, NewQbUnit)
    assert unit.label == "New Unit 3"
    assert new_units_3.csv_column_uri_template is None


def test_measures_loading():
    """
    Test that multi-measure dimensions with existing and new measures can be successfully loaded using the new
    info.json v1.1 syntax using all possible configuration types.
    """
    data = pd.read_csv(
        get_test_cases_dir() / "configloaders" / "infojson1-1" / "measures.csv"
    )
    cube, json_schema_validation_error = get_cube_from_info_json(
        get_test_cases_dir() / "configloaders" / "infojson1-1" / "measures.json",
        data,
    )

    existing_measures = _get_column_definition(cube, "Existing Measures")
    new_measures = _get_column_definition(cube, "New Measures")
    new_measures_2 = _get_column_definition(cube, "New Measures 2")
    new_measures_3 = _get_column_definition(cube, "New Measures 3")

    assert existing_measures is not None
    assert isinstance(existing_measures.component, QbMultiMeasureDimension)
    assert len(existing_measures.component.measures) == 1
    measure = existing_measures.component.measures[0]
    assert isinstance(measure, ExistingQbMeasure)
    assert measure.measure_uri == "http://example.com/measures/some-existing-measure"
    assert (
        existing_measures.csv_column_uri_template
        == "http://example.com/measures/{+existing_measures}"
    )

    assert new_measures is not None
    assert isinstance(new_measures.component, QbMultiMeasureDimension)
    assert len(new_measures.component.measures) == 1
    measure = new_measures.component.measures[0]
    assert isinstance(measure, NewQbMeasure)
    assert measure.label == "Some Measure 1"
    assert new_measures.csv_column_uri_template is None

    assert new_measures_2 is not None
    assert isinstance(new_measures_2.component, QbMultiMeasureDimension)
    assert len(new_measures_2.component.measures) == 1
    measure = new_measures_2.component.measures[0]
    assert isinstance(measure, NewQbMeasure)
    assert measure.label == "Some Measure 2"
    assert measure.description == "Some Measure 2 Comment"
    assert measure.uri_safe_identifier_override == "some-measure-2"
    assert measure.source_uri == "http://example.com/measures/defs/some-measure-2"
    assert new_measures_2.csv_column_uri_template is None

    assert new_measures_3 is not None
    assert isinstance(new_measures_3.component, QbMultiMeasureDimension)
    assert len(new_measures_3.component.measures) == 1
    measure = new_measures_3.component.measures[0]
    assert isinstance(measure, NewQbMeasure)
    assert measure.label == "Some Measure 3"
    assert new_measures_3.csv_column_uri_template is None


def test_observation_value_loading():
    """
    Test that single and multi-measure observation value columns can be successfully loaded using the new
    info.json v1.1 syntax using all possible configuration types.
    """
    data = pd.read_csv(info_json_1_1_test_cases_dir / "observations.csv")
    cube, json_schema_validation_error = get_cube_from_info_json(
        info_json_1_1_test_cases_dir / "observations.json",
        data,
    )

    single_measure = _get_column_definition(cube, "Single Measure Value")
    single_measure_2 = _get_column_definition(cube, "Single Measure Value 2")
    multi_measure = _get_column_definition(cube, "Multi Measure Value")
    multi_measure_2 = _get_column_definition(cube, "Multi Measure Value 2")

    assert single_measure is not None
    assert isinstance(single_measure.component, QbSingleMeasureObservationValue)
    assert isinstance(single_measure.component.measure, ExistingQbMeasure)
    assert (
        single_measure.component.measure.measure_uri
        == "http://gss-data.org.uk/def/measure/trade"
    )
    assert isinstance(single_measure.component.unit, ExistingQbUnit)
    assert (
        single_measure.component.unit.unit_uri
        == "http://gss-data.org.uk/def/concept/measurement-units/gbp-million"
    )
    assert single_measure.component.data_type == "double"
    assert single_measure.csv_column_uri_template is None

    assert single_measure_2 is not None
    assert isinstance(single_measure_2.component, QbSingleMeasureObservationValue)
    assert isinstance(single_measure_2.component.measure, NewQbMeasure)
    assert single_measure_2.component.measure.label == "New Measure 2"
    assert isinstance(single_measure_2.component.unit, NewQbUnit)
    assert single_measure_2.component.unit.label == "New Unit 2"
    assert isinstance(single_measure_2.component.unit.base_unit, ExistingQbUnit)
    assert (
        single_measure_2.component.unit.base_unit.unit_uri
        == "http://gss-data.org.uk/def/concept/measurement-units/some-unit"
    )
    assert single_measure_2.component.unit.base_unit_scaling_factor == 7
    assert single_measure_2.component.data_type == "decimal"
    assert single_measure_2.csv_column_uri_template is None

    assert multi_measure is not None
    assert isinstance(multi_measure.component, QbMultiMeasureObservationValue)
    assert isinstance(multi_measure.component.unit, ExistingQbUnit)
    assert (
        multi_measure.component.unit.unit_uri
        == "http://gss-data.org.uk/def/concept/measurement-units/gbp-billions"
    )
    assert multi_measure.component.data_type == "decimal"
    assert multi_measure.csv_column_uri_template is None

    assert multi_measure_2 is not None
    assert isinstance(multi_measure_2.component, QbMultiMeasureObservationValue)
    assert multi_measure_2.component.unit is None
    assert multi_measure_2.component.data_type == "short"
    assert multi_measure_2.csv_column_uri_template is None


def test_dimension_loading():
    """
    Test that existing and new dimensions can be successfully loaded using the new info.json v1.1 syntax using all
    possible configuration types.
    """
    data = pd.read_csv(info_json_1_1_test_cases_dir / "dimensions.csv")
    cube, json_schema_validation_error = get_cube_from_info_json(
        info_json_1_1_test_cases_dir / "dimensions.json",
        data,
    )

    existing_dimension = _get_column_definition(cube, "Existing Dimension")
    new_dimension = _get_column_definition(cube, "New Dimension")
    new_dimension_2 = _get_column_definition(cube, "New Dimension 2")
    new_dimension_3 = _get_column_definition(cube, "New Dimension 3")
    new_dimension_4 = _get_column_definition(cube, "New Dimension 4")
    new_dimension_5 = _get_column_definition(cube, "New Dimension 5")
    new_dimension_6 = _get_column_definition(cube, "New Dimension 6")

    assert existing_dimension is not None
    assert isinstance(existing_dimension.component, ExistingQbDimension)
    assert (
        existing_dimension.component.dimension_uri
        == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
    )
    assert (
        existing_dimension.csv_column_uri_template
        == "http://reference.data.gov.uk/id/{period}"
    )

    assert new_dimension is not None
    assert isinstance(new_dimension.component, NewQbDimension)
    assert new_dimension.component.label == "New Dimension"
    assert isinstance(new_dimension.component.code_list, NewQbCodeList)
    assert len(new_dimension.component.code_list.concepts) == 1
    assert new_dimension.component.code_list.concepts[0].label == "Some Value"
    assert new_dimension.csv_column_uri_template is None

    assert new_dimension_2 is not None
    assert isinstance(new_dimension_2.component, NewQbDimension)
    assert new_dimension_2.component.label == "New Dimension 2 Label"
    assert new_dimension_2.component.uri_safe_identifier_override == "new-dimension-2"
    assert new_dimension_2.component.description == "New Dimension 2 Comment"
    assert (
        new_dimension_2.component.parent_dimension_uri
        == "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
    )
    assert new_dimension_2.component.code_list is None
    assert (
        new_dimension_2.csv_column_uri_template
        == "http://reference.data.gov.uk/id/{period}"
    )

    assert new_dimension_3 is not None
    assert isinstance(new_dimension_3.component, NewQbDimension)
    assert new_dimension_3.component.label == "New Dimension 3"
    assert isinstance(new_dimension_3.component.code_list, NewQbCodeList)
    assert len(new_dimension_3.component.code_list.concepts) == 1
    assert new_dimension_3.component.code_list.concepts[0].label == "Some Value"
    assert new_dimension_3.csv_column_uri_template is None

    assert new_dimension_4 is not None
    assert isinstance(new_dimension_4.component, NewQbDimension)
    assert new_dimension_4.component.label == "New Dimension 4"
    assert isinstance(new_dimension_4.component.code_list, ExistingQbCodeList)
    assert (
        new_dimension_4.component.code_list.concept_scheme_uri
        == "http://data.europa.eu/nuts"
    )
    assert (
        new_dimension_4.csv_column_uri_template
        == "http://data.europa.eu/nuts/{+new_dimension_4}"
    )

    assert new_dimension_5 is not None
    assert isinstance(new_dimension_5.component, NewQbDimension)
    assert new_dimension_5.component.label == "New Dimension 5"
    assert isinstance(new_dimension_5.component.code_list, NewQbCodeListInCsvW)
    assert (
        new_dimension_5.component.code_list.schema_metadata_file_path
        == info_json_1_1_test_cases_dir
        / "codelists"
        / "new-dimension-5.csv-metadata.json"
    )
    assert new_dimension_5.csv_column_uri_template is None

    assert new_dimension_6 is not None
    assert isinstance(new_dimension_6.component, NewQbDimension)
    assert new_dimension_6.component.label == "New Dimension 6"
    assert isinstance(new_dimension_6.component.code_list, NewQbCodeList)
    assert len(new_dimension_6.component.code_list.concepts) == 1
    assert new_dimension_6.component.code_list.concepts[0].label == "Some Value"
    assert new_dimension_6.csv_column_uri_template is None


def test_attribute_loading():
    """
    Test that existing and new attributes can be successfully loaded using the new info.json v1.1 syntax using all
    possible configuration types.
    """
    data = pd.read_csv(info_json_1_1_test_cases_dir / "attributes.csv")
    cube, json_schema_validation_error = get_cube_from_info_json(
        info_json_1_1_test_cases_dir / "attributes.json",
        data,
    )

    existing_marker = _get_column_definition(cube, "Existing Marker")
    existing_marker_2 = _get_column_definition(cube, "Existing Marker 2")
    existing_marker_3 = _get_column_definition(cube, "Existing Marker 3")
    new_marker = _get_column_definition(cube, "New Marker")
    new_marker_2 = _get_column_definition(cube, "New Marker 2")
    new_marker_3 = _get_column_definition(cube, "New Marker 3")
    new_marker_4 = _get_column_definition(cube, "New Marker 4")
    new_marker_5 = _get_column_definition(cube, "New Marker 5")

    assert existing_marker is not None
    assert isinstance(existing_marker.component, ExistingQbAttribute)
    assert (
        existing_marker.component.attribute_uri
        == "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
    )
    assert (
        existing_marker.csv_column_uri_template
        == "http://gss-data.org.uk/def/concept/cogs-markers/{marker}"
    )
    assert len(existing_marker.component.new_attribute_values) == 0
    assert existing_marker.component.is_required

    assert existing_marker_2 is not None
    assert isinstance(existing_marker_2.component, ExistingQbAttribute)
    assert (
        existing_marker_2.component.attribute_uri
        == "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
    )
    assert len(existing_marker_2.component.new_attribute_values) == 1
    assert (
        existing_marker_2.component.new_attribute_values[0].label == "Some Marker Value"
    )
    assert not existing_marker_2.component.is_required
    assert existing_marker_2.csv_column_uri_template is None

    assert existing_marker_3 is not None
    assert isinstance(existing_marker_3.component, ExistingQbAttribute)
    assert (
        existing_marker_3.component.attribute_uri
        == "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
    )
    assert len(existing_marker_3.component.new_attribute_values) == 1
    assert (
        existing_marker_3.component.new_attribute_values[0].label
        == "Some Incorrect Marker Value"
    )
    assert not existing_marker_3.component.is_required
    assert existing_marker_3.csv_column_uri_template is None

    assert new_marker is not None
    assert isinstance(new_marker.component, NewQbAttribute)
    assert new_marker.component.label == "New Marker"
    assert len(new_marker.component.new_attribute_values) == 1
    assert new_marker.component.new_attribute_values[0].label == "Some Marker Value"
    assert new_marker.component.is_required
    assert new_marker.csv_column_uri_template is None

    assert new_marker_2 is not None
    assert isinstance(new_marker_2.component, NewQbAttribute)
    assert new_marker_2.component.label == "New Marker 2"
    assert new_marker_2.component.uri_safe_identifier_override == "new-marker-2"
    assert new_marker_2.component.description == "This is new marker 2"
    assert (
        new_marker_2.component.parent_attribute_uri
        == "http://gss-data.org.uk/def/trade/property/attribute/marker"
    )
    assert (
        new_marker_2.component.source_uri
        == "http://example.org/attributes/markers/new-marker-2"
    )
    assert len(new_marker_2.component.new_attribute_values) == 1
    assert new_marker_2.component.new_attribute_values[0].label == "Some Marker Value"
    assert not new_marker_2.component.is_required
    assert new_marker_2.csv_column_uri_template is None

    assert new_marker_3 is not None
    assert isinstance(new_marker_3.component, NewQbAttribute)
    assert new_marker_3.component.label == "New Marker 3"
    assert len(new_marker_3.component.new_attribute_values) == 1
    assert (
        new_marker_3.component.new_attribute_values[0].label
        == "Some Incorrect Marker Value"
    )
    assert not new_marker_3.component.is_required
    assert new_marker_3.csv_column_uri_template is None

    assert new_marker_4 is not None
    assert isinstance(new_marker_4.component, NewQbAttribute)
    assert new_marker_4.component.label == "New Marker 4"
    assert len(new_marker_4.component.new_attribute_values) == 0
    assert not new_marker_4.component.is_required
    assert (
        new_marker_4.csv_column_uri_template
        == "http://example.org/attributes/new-marker-4/{+new_marker_4}"
    )

    assert new_marker_5 is not None
    assert isinstance(new_marker_5.component, NewQbAttribute)
    assert new_marker_5.component.label == "New Marker 5"
    assert len(new_marker_5.component.new_attribute_values) == 1
    assert new_marker_5.component.new_attribute_values[0].label == "Some Marker Value"
    assert not new_marker_5.component.is_required
    assert new_marker_5.csv_column_uri_template is None


def _get_column_definition(cube: Cube, column_title: str) -> QbColumn:
    return first(
        cube.columns,
        lambda x: isinstance(x, QbColumn) and x.csv_column_title == column_title,
    )


if __name__ == "__main__":
    pytest.main()
