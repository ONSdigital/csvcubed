import pandas as pd
import pytest

from csvcubed.definitions import QB_MEASURE_TYPE_DIMENSION_URI, SDMX_ATTRIBUTE_UNIT_URI
from csvcubed.models.cube.columns import SuppressedCsvColumn
from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.attribute import (
    ExistingQbAttribute,
    NewQbAttribute,
)
from csvcubed.models.cube.qb.components.attributevalue import NewQbAttributeValue
from csvcubed.models.cube.qb.components.codelist import (
    ExistingQbCodeList,
    NewQbCodeList,
)
from csvcubed.models.cube.qb.components.concept import NewQbConcept
from csvcubed.models.cube.qb.components.dimension import (
    ExistingQbDimension,
    NewQbDimension,
)
from csvcubed.models.cube.qb.components.measure import ExistingQbMeasure, NewQbMeasure
from csvcubed.models.cube.qb.components.measuresdimension import QbMultiMeasureDimension
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unit import ExistingQbUnit, NewQbUnit
from csvcubed.models.cube.qb.components.unitscolumn import QbMultiUnits
from csvcubed.models.cube.uristyle import URIStyle
from csvcubed.writers.helpers.qbwriter.urihelper import UriHelper
from csvcubed.writers.helpers.skoscodelistwriter.constants import SCHEMA_URI_IDENTIFIER
from tests.unit.writers.qbwriter.test_qbwriter import TestQbMeasure

empty_cube = Cube(CatalogMetadata("Cube Name"), pd.DataFrame, [])
empty_cube_uri_helper = UriHelper(empty_cube)


def test_generating_concept_uri_template_from_legacy_global_concept_scheme_uri():
    """
    Given a globally defined skos:ConceptScheme's URI, generate the URI template for a column which maps the
    column's value to a concept defined inside the concept scheme.
    """
    column = SuppressedCsvColumn("Some Column")
    code_list = ExistingQbCodeList(
        "http://base-uri/concept-scheme/this-concept-scheme-name"
    )

    actual_concept_template_uri = (
        empty_cube_uri_helper._get_default_value_uri_for_code_list_concepts(
            column, code_list
        )
    )
    assert (
        "http://base-uri/concept-scheme/this-concept-scheme-name/{+some_column}"
        == actual_concept_template_uri
    )


def test_generating_concept_uri_template_from_legacy_local_concept_scheme_uri():
    """
    Given a dataset-local skos:ConceptScheme's URI, generate the URI template for a column which maps the
    column's value to a concept defined inside the concept scheme.
    """
    column = SuppressedCsvColumn("Some Column")
    code_list = ExistingQbCodeList(
        "http://base-uri/dataset-name#scheme/that-concept-scheme-name"
    )

    actual_concept_template_uri = (
        empty_cube_uri_helper._get_default_value_uri_for_code_list_concepts(
            column, code_list
        )
    )
    assert (
        "http://base-uri/dataset-name#concept/that-concept-scheme-name/{+some_column}"
        == actual_concept_template_uri
    )


def test_generating_concept_uri_template_from_csvcubed_concept_scheme_uri():
    """
    Given a csvcubed-style skos:ConceptScheme's URI, generate the URI template for a column which maps the
    column's value to a concept defined inside the concept scheme.
    """
    column = SuppressedCsvColumn("Some Column")
    code_list = ExistingQbCodeList(
        f"http://base-uri/concept-scheme#{SCHEMA_URI_IDENTIFIER}"
    )

    actual_concept_template_uri = (
        empty_cube_uri_helper._get_default_value_uri_for_code_list_concepts(
            column, code_list
        )
    )
    assert (
        "http://base-uri/concept-scheme#{+some_column}" == actual_concept_template_uri
    )


def test_generating_concept_uri_template_from_unexpected_concept_scheme_uri():
    """
    Given a skos:ConceptScheme's URI *that does not follow the global or dataset-local conventions* used in our
    tooling, return the column's value as our best guess at the concept's URI.
    """
    column = SuppressedCsvColumn("Some Column")
    code_list = ExistingQbCodeList(
        "http://base-uri/dataset-name#codes/that-concept-scheme-name"
    )

    actual_concept_template_uri = (
        empty_cube_uri_helper._get_default_value_uri_for_code_list_concepts(
            column, code_list
        )
    )
    assert "{+some_column}" == actual_concept_template_uri


def test_default_property_value_uris_existing_dimension_column():
    """
    When an existing dimension is used, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        ExistingQbDimension("http://base-uri/dimensions/existing-dimension"),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "http://base-uri/dimensions/existing-dimension" == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_new_dimension_column_without_code_list():
    """
    When a new dimension is defined without a code list, we can provide the `propertyUrl`,
    but we cannot guess the `valueUrl`.
    """
    column = QbColumn("Some Column", NewQbDimension("Some New Dimension"))
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "cube-name.csv#dimension/some-new-dimension" == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_new_dimension_column_with_code_list():
    """
    When an new dimension is defined with a code list, we can provide the `propertyUrl` and the `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        NewQbDimension(
            "Some New Dimension",
            code_list=ExistingQbCodeList("http://base-uri/concept-scheme/this-scheme"),
        ),
    )

    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)

    assert "cube-name.csv#dimension/some-new-dimension" == default_property_uri
    assert (
        "http://base-uri/concept-scheme/this-scheme/{+some_column}" == default_value_uri
    )


def test_default_property_value_uris_new_dimension_column_with_new_code_list():
    """
    When a new dimension is defined with a new code list, by default it should provide standard-formatted property and value Urls
    """
    column = QbColumn(
        "Some Column",
        NewQbDimension(
            "Some New Dimension",
            code_list=NewQbCodeList(CatalogMetadata("Some Catalog"), []),
        ),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "cube-name.csv#dimension/some-new-dimension" == default_property_uri
    assert "some-catalog.csv#{+some_column}" == default_value_uri


def test_default_property_value_uris_new_dimension_column_with_new_code_list_for_cube_WithoutFileExtensions_uri_style():
    """
    When a new dimension is defined with a new code list, and the cube has a defined uri_style of WithoutFileExtensions,
    it should provide property and value Urls which follow the cube's uri style
    """

    uri_styled_cube = Cube(
        CatalogMetadata("Cube Name"), pd.DataFrame, [], URIStyle.WithoutFileExtensions
    )
    uri_styled_uri_helper = UriHelper(uri_styled_cube)

    column = QbColumn(
        "Some Column",
        NewQbDimension(
            "Some New Dimension",
            code_list=NewQbCodeList(CatalogMetadata("Some Catalog"), []),
        ),
    )

    (
        default_property_uri,
        default_value_uri,
    ) = uri_styled_uri_helper.get_default_property_value_uris_for_column(column)

    assert "cube-name#dimension/some-new-dimension" == default_property_uri
    assert "some-catalog#{+some_column}" == default_value_uri


def test_default_property_value_uris_existing_attribute_existing_values():
    """
    When an existing attribute is used, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        ExistingQbAttribute("http://base-uri/attributes/existing-attribute"),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "http://base-uri/attributes/existing-attribute" == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_existing_attribute_new_values():
    """
    When an existing attribute is used, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        ExistingQbAttribute("http://base-uri/attributes/existing-attribute"),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "http://base-uri/attributes/existing-attribute" == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_new_attribute_existing_values():
    """
    When a new attribute is defined, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn("Some Column", NewQbAttribute("This New Attribute"))
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "cube-name.csv#attribute/this-new-attribute" == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_new_attribute_new_values():
    """
    When a new attribute is defined, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        NewQbAttribute(
            "This New Attribute",
            code_list=NewQbCodeList(
                CatalogMetadata("This New Attribute"), [NewQbConcept("Something")]
            ),
        ),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert "cube-name.csv#attribute/this-new-attribute" == default_property_uri
    assert (
        "cube-name.csv#attribute/this-new-attribute/{+some_column}" == default_value_uri
    )


def test_default_property_value_uris_multi_units_all_new():
    """
    When a QbMultiUnits component is defined using only new/locally defined units, we can provide the
    `propertyUrl` and the `valueUrl`.
    """
    column = QbColumn("Some Column", QbMultiUnits([NewQbUnit("Some New Unit")]))
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert SDMX_ATTRIBUTE_UNIT_URI == default_property_uri
    assert "cube-name.csv#unit/{+some_column}" == default_value_uri


def test_default_property_value_uris_multi_units_all_existing():
    """
    When a QbMultiUnits component is defined using just existing units, we can provide the `propertyUrl` and
    `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        QbMultiUnits([ExistingQbUnit("http://base-uri/units/existing-unit")]),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert SDMX_ATTRIBUTE_UNIT_URI == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_multi_units_local_and_existing():
    """
    When a QbMultiUnits component is defined using a mixture of existing units and new units, we can't provide
    an appropriate and consistent `valueUrl`.

    An exception is raised when this is attempted.
    """
    column = QbColumn(
        "Some Column",
        QbMultiUnits(
            [
                NewQbUnit("Some New Unit"),
                ExistingQbUnit("http://base-uri/units/existing-unit"),
            ]
        ),
    )
    with pytest.raises(Exception) as exception:

        def fetch_exception():
            empty_cube_uri_helper.get_default_property_value_uris_for_column(column)

        fetch_exception()


def test_default_property_value_uris_multi_measure_all_new():
    """
    When a QbMultiMeasureDimension component is defined using only new/locally defined measures,
    we can provide the `propertyUrl` and the `valueUrl`.
    """
    column = QbColumn(
        "Some Column", QbMultiMeasureDimension([NewQbMeasure("Some New Measure")])
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert QB_MEASURE_TYPE_DIMENSION_URI == default_property_uri
    assert "cube-name.csv#measure/{+some_column}" == default_value_uri


def test_default_property_value_uris_multi_measure_all_existing():
    """
    When a QbMultiUnits component is defined using just existing units, we can provide the `propertyUrl` and
    `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        QbMultiMeasureDimension(
            [ExistingQbMeasure("http://base-uri/measures/existing-measure")]
        ),
        csv_column_uri_template="http://base-uri/measures/{+some_column}",
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert QB_MEASURE_TYPE_DIMENSION_URI == default_property_uri
    assert "http://base-uri/measures/{+some_column}" == default_value_uri


def test_default_property_value_uris_multi_measure_local_and_existing():
    """
    When a QbMultiUnits component is defined using a mixture of existing units and new units, we can't provide
    an appropriate and consistent `valueUrl`.

    An exception is raised when this is attempted.
    """
    column = QbColumn(
        "Some Column",
        QbMultiMeasureDimension(
            [
                NewQbMeasure("Some New Measure"),
                ExistingQbMeasure("http://base-uri/measures/existing-measure"),
            ]
        ),
    )

    with pytest.raises(Exception) as exception:

        def fetch_exception():
            empty_cube_uri_helper.get_default_property_value_uris_for_column(column)

        fetch_exception()


def test_default_property_value_uris_single_measure_obs_val():
    """
    There should be no `propertyUrl` or `valueUrl` for a `QbObservationValue`.
    """
    column = QbColumn(
        "Some Column",
        QbObservationValue(
            unit=NewQbUnit("New Unit"), measure=NewQbMeasure("New Qb Measure")
        ),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_cube_uri_helper.get_default_property_value_uris_for_column(column)
    assert default_property_uri == "cube-name.csv#measure/new-qb-measure"
    assert default_value_uri is None


def test_default_property_value_uris_multi_measure_obs_val():
    """
    There should be no `valueUrl` for a `QbObservationValue`.
    """
    column = QbColumn("Some Column", QbObservationValue())

    cube = Cube(
        CatalogMetadata("Cube Name"),
        pd.DataFrame({"Measure": ["kg"]}),
        [QbColumn("Measure", QbMultiMeasureDimension([NewQbMeasure("kg")]))],
    )
    uri_helper = UriHelper(cube)

    (
        default_property_uri,
        default_value_uri,
    ) = uri_helper.get_default_property_value_uris_for_column(column)
    assert default_property_uri == "cube-name.csv#measure/{+measure}"
    assert default_value_uri is None


def test_default_property_value_uris_multi_existing_measure_obs_val():
    """
    The `propertyUrl` for a multi-existing-measure observation value should match the measure column's
    value URI template.
    """
    column = QbColumn("Some Column", QbObservationValue())

    cube = Cube(
        CatalogMetadata("Cube Name"),
        pd.DataFrame({"Measure": ["kg"]}),
        [
            QbColumn(
                "Measure",
                QbMultiMeasureDimension(
                    [ExistingQbMeasure("http://some-existing-measures/kg")]
                ),
                csv_column_uri_template="http://some-existing-measures/{+measure}",
            )
        ],
    )
    uri_helper = UriHelper(cube)

    (
        default_property_uri,
        default_value_uri,
    ) = uri_helper.get_default_property_value_uris_for_column(column)
    assert default_property_uri == "http://some-existing-measures/{+measure}"
    assert default_value_uri is None


def test_get_observation_value_col_for_title():
    """
    Ensure that the column title for the QbObservationValue returned matches the input column title.
    """
    expected_obs_val_col = QbColumn(
        "Some Obs Val",
        QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
    )

    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            expected_obs_val_col,
        ],
    )

    uri_helper = UriHelper(cube)
    actual_obs_val_col = uri_helper._get_observation_value_col_for_title("Some Obs Val")

    assert actual_obs_val_col == expected_obs_val_col


def test_get_observation_value_col_for_title_when_col_title_is_invalid():
    """
    Ensure that the invalid column title raises an exception.
    """

    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Invalid Col Title", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    uri_helper = UriHelper(cube)
    with pytest.raises(Exception) as err:
        uri_helper._get_observation_value_col_for_title("Invalid Col Title")

    assert (
        str(err.value)
        == 'Could not find one observation value column. Found 0 for title: "Invalid Col Title".'
    )


def test_get_observation_uri_for_pivoted_shape_data_set_new_qbmeasure():
    """
    Ensures that the observation value's URI is returned for an observation with a new Qbmeasure.
    """
    obs_val_column = QbColumn(
        "Some Obs Val",
        QbObservationValue(NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")),
    )
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            obs_val_column,
        ],
    )
    expected_observation_uri = "cube.csv#obs/{some_dimension}@some-measure"

    uri_helper = UriHelper(cube)
    actual_observation_uri = uri_helper.get_observation_uri_for_pivoted_shape_data_set(
        obs_val_column
    )

    assert actual_observation_uri == expected_observation_uri


def test_get_observation_uri_for_pivoted_shape_data_set_existing_qbmeasure():
    """
    Ensures that the observation value's URI is returned for an observation with a new Qbmeasure.
    """
    obs_val_column = QbColumn(
        "Some Obs Val",
        QbObservationValue(
            ExistingQbMeasure("http://example.com/measures/existing_measure"),
            NewQbUnit("Some Unit"),
        ),
    )

    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            obs_val_column,
        ],
    )
    expected_observation_uri = (
        "cube.csv#obs/{some_dimension}@http-//example-com/measures/existing_measure"
    )

    uri_helper = UriHelper(cube)
    actual_observation_uri = uri_helper.get_observation_uri_for_pivoted_shape_data_set(
        obs_val_column
    )

    assert actual_observation_uri == expected_observation_uri


def test_get_observation_uri_for_pivoted_shape_data_set_raise_exception():
    """
    Ensures that the observation value's URI raises an exception when given an unhandled QbMeasure type.
    """

    obs_val_column = QbColumn(
        "Some Obs Val",
        QbObservationValue(
            TestQbMeasure("Some Measure"),
            NewQbUnit("Some Unit"),
        ),
    )

    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            obs_val_column,
        ],
    )
    obs_val_measure = obs_val_column.structural_definition.measure

    uri_helper = UriHelper(cube)
    with pytest.raises(Exception) as exception:
        uri_helper.get_observation_uri_for_pivoted_shape_data_set(obs_val_column)
        assert (
            str(exception.value) == f"Unhandled QbMeasure type {type(obs_val_measure)}"
        )


def test_get_pivoted_cube_slice_uri():
    """
    Ensures that the pivoted shape cube slice URI is returned.
    """

    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )

    uri_helper = UriHelper(cube)

    expected_slice_uri = "cube.csv#slice/{some_dimension}"
    actual_slice_uri = uri_helper._get_pivoted_cube_slice_uri()

    assert actual_slice_uri == expected_slice_uri


def test_get_about_url_for_pivoted_shape_cube():
    """
    Ensures that the pivoted shape cube about URL is returned.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )

    uri_helper = UriHelper(cube)
    expected_about_url = "cube.csv#slice/{some_dimension}"
    actual_about_url = uri_helper.get_about_url()

    assert actual_about_url == expected_about_url


def test_get_about_url_for_standard_shape_cube():
    """
    Ensures that the standard shape cube about URL is returned.
    """

    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    unit=NewQbUnit("Some Unit"),
                ),
            ),
            QbColumn(
                "Some Measure",
                QbMultiMeasureDimension([NewQbMeasure("New Measure")]),
            ),
        ],
    )

    uri_helper = UriHelper(cube)

    expected_about_url = "cube.csv#obs/{some_dimension}@{some_measure}"
    actual_about_url = uri_helper.get_about_url()

    assert actual_about_url == expected_about_url


def test_about_url_generation():
    """
    Ensuring that when an aboutUrl is defined for a non-multimeasure cube, the resulting URL
    is built in the order in which dimensions appear in the cube.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Local Dimension": ["D", "E", "F"],
            "Value": [2, 2, 2],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Existing Dimension",
            ExistingQbDimension("https://example.org/dimensions/existing_dimension"),
        ),
        QbColumn(
            "Local Dimension",
            NewQbDimension.from_data("Name of New Dimension", data["Local Dimension"]),
        ),
        QbColumn(
            "Value",
            QbObservationValue(
                ExistingQbMeasure("http://example.com/measures/existing_measure"),
                NewQbUnit("New Unit"),
            ),
        ),
    ]

    cube = Cube(metadata, data, columns)

    actual_about_url = UriHelper(cube).get_about_url()
    expected_about_url = "some-dataset.csv#slice/{existing_dimension},{local_dimension}"
    assert actual_about_url == expected_about_url


def test_about_url_generation_with_multiple_measures():
    """
    Ensuring that when an aboutUrl is defined for a multi-measure cube, the resulting URL
    is built in the order in which dimensions appear in the cube except for the multi-measure
    dimensions which are appended to the end of the URL.
    """
    data = pd.DataFrame(
        {
            "Measure": ["People", "Children", "Adults"],
            "Existing Dimension": ["A", "B", "C"],
            "Value": [2, 2, 2],
            "Local Dimension": ["D", "E", "F"],
            "Units": ["Percent", "People", "People"],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Measure", QbMultiMeasureDimension.new_measures_from_data(data["Measure"])
        ),
        QbColumn(
            "Existing Dimension",
            ExistingQbDimension("https://example.org/dimensions/existing_dimension"),
        ),
        QbColumn(
            "Local Dimension",
            NewQbDimension.from_data("Name of New Dimension", data["Local Dimension"]),
        ),
        QbColumn("Value", QbObservationValue("number")),
        QbColumn("Units", QbMultiUnits.new_units_from_data(data["Units"])),
    ]

    cube = Cube(metadata, data, columns)

    actual_about_url = UriHelper(cube).get_about_url()
    expected_about_url = "some-dataset.csv#slice/{existing_dimension},{local_dimension}"
    assert actual_about_url == expected_about_url


if __name__ == "__main__":
    pytest.main()
