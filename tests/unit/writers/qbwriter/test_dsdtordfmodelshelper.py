import pytest
from csvcubedmodels import rdf

from csvcubed.models.cube import (
    URIStyle,
    Cube,
    CatalogMetadata,
    QbColumn,
    ExistingQbDimension,
    ExistingQbAttribute,
    QbObservationValue,
    ExistingQbMeasure,
    ExistingQbUnit,
    NewQbUnit,
    NewQbMeasure,
    NewQbAttribute,
    NewQbDimension,
)
from csvcubed.writers.helpers.qbwriter.dsdtordfmodelshelper import DsdToRdfModelsHelper
from csvcubed.writers.helpers.qbwriter.urihelper import UriHelper
from .testhelpers import (
    assert_component_defined,
    get_standard_cube_for_columns,
)


def test_structure_defined():
    cube = get_standard_cube_for_columns(
        [
            QbColumn(
                "Country",
                ExistingQbDimension("http://example.org/dimensions/country"),
            ),
            QbColumn(
                "Marker",
                ExistingQbAttribute("http://example.org/attributes/marker"),
            ),
            QbColumn(
                "Observed Value",
                QbObservationValue(
                    ExistingQbMeasure("http://example.org/units/some-existing-measure"),
                    ExistingQbUnit("http://example.org/units/some-existing-unit"),
                ),
            ),
        ]
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()

    assert dataset is not None

    assert dataset.structure is not None
    assert type(dataset.structure) == rdf.qb.DataStructureDefinition

    assert dataset.structure.componentProperties is not None

    assert_component_defined(dataset, "country")
    assert_component_defined(dataset, "marker")
    assert_component_defined(dataset, "unit")
    assert_component_defined(dataset, "some-existing-measure")


def test_structure_uri():
    cube = Cube(CatalogMetadata("Cube Name"))
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual = dsd_helper._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name.csv#")


def test_structure_uri_standard_pattern():
    cube = Cube(CatalogMetadata("Cube Name"), uri_style=URIStyle.Standard)
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual = dsd_helper._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name.csv#")


def test_structure_uri_without_file_extensions_pattern():
    cube = Cube(CatalogMetadata("Cube Name"), uri_style=URIStyle.WithoutFileExtensions)
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual = dsd_helper._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name#")


def test_get_cross_measures_slice_key_for_new_dimension():
    """
    Ensure that given a cube with NewQbDimension, the function returns the correct slice key.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual_slice_key = dsd_helper._get_cross_measures_slice_key()
    assert str(actual_slice_key.uri) == "cube.csv#slice/cross-measures"

    component_properties = list(actual_slice_key.componentProperties)
    assert len(component_properties) == 1
    assert str(component_properties[0].uri) == "cube.csv#dimension/some-dimension"


def test_get_cross_measures_slice_key_for_existing_dimension():
    """
    Ensure that given a cube with ExistingQbDimension, the function returns the correct slice key.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn(
                "Some Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension"
                ),
            ),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual_slice_key = dsd_helper._get_cross_measures_slice_key()
    assert str(actual_slice_key.uri) == "cube.csv#slice/cross-measures"

    component_properties = list(actual_slice_key.componentProperties)
    assert len(component_properties) == 1
    assert (
        str(component_properties[0].uri)
        == "https://example.org/dimensions/existing_dimension"
    )


if __name__ == "__main__":
    pytest.main()
