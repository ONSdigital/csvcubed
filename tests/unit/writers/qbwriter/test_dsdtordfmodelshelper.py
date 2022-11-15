import pandas as pd
import pytest
from csvcubedmodels import rdf
from rdflib import URIRef, Graph, RDFS, Literal

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.arbitraryrdf import RdfSerialisationHint
from csvcubed.models.cube.qb.components.arbitraryrdf import TripleFragment
from csvcubed.models.cube.qb.components.attribute import (
    NewQbAttribute,
    ExistingQbAttribute,
)
from csvcubed.models.cube.qb.components.dimension import (
    NewQbDimension,
    ExistingQbDimension,
)
from csvcubed.models.cube.qb.components.measure import NewQbMeasure, ExistingQbMeasure
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unitscolumn import NewQbUnit, ExistingQbUnit
from csvcubed.models.cube.uristyle import URIStyle
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
    """
    Ensure that the data structure definition's URI is defined relative to the cube's CSV file.
    """
    cube = Cube(CatalogMetadata("Cube Name"))
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual = dsd_helper._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name.csv#")


def test_structure_uri_standard_pattern():
    """
    Ensure that the data structure definition's URI is defined relative to the cube's CSV file when
    the URIStyle is set to output in the standard format (i.e. with file extensions).
    """

    cube = Cube(CatalogMetadata("Cube Name"), uri_style=URIStyle.Standard)
    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))

    actual = dsd_helper._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name.csv#")


def test_structure_uri_without_file_extensions_pattern():
    """
    Ensure that the data structure definition's URI is defined relative to the cube's CSV file even when
    the URIStyle is set to output URIs without file extensions.
    """
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


def test_arbitrary_rdf_serialisation_existing_attribute():
    """
    Test that when arbitrary RDF is specified against an Existing Attribute, it is serialised correctly.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [1, 2, 3],
            "Existing Attribute": ["Provisional", "Final", "Provisional"],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "Existing Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension"
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
            QbColumn(
                "Existing Attribute",
                ExistingQbAttribute(
                    "http://some-existing-attribute-uri",
                    arbitrary_rdf=[
                        TripleFragment(RDFS.label, "Existing Attribute Component")
                    ],
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#component/existing-attribute"),
        RDFS.label,
        Literal("Existing Attribute Component"),
    ) in graph


def test_arbitrary_rdf_serialisation_new_attribute():
    """
    Test that when arbitrary RDF is specified against a New Attribute, it is serialised correctly.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [1, 2, 3],
            "New Attribute": ["Provisional", "Final", "Provisional"],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "Existing Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension"
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
            QbColumn(
                "Existing Attribute",
                NewQbAttribute.from_data(
                    "New Attribute",
                    data["New Attribute"],
                    arbitrary_rdf=[
                        TripleFragment(RDFS.label, "New Attribute Property"),
                        TripleFragment(
                            RDFS.label,
                            "New Attribute Component",
                            RdfSerialisationHint.Component,
                        ),
                    ],
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#attribute/new-attribute"),
        RDFS.label,
        Literal("New Attribute Property"),
    ) in graph

    assert (
        URIRef("some-dataset.csv#component/new-attribute"),
        RDFS.label,
        Literal("New Attribute Component"),
    ) in graph


def test_arbitrary_rdf_serialisation_existing_dimension():
    """
    Test that when arbitrary RDF is specified against an Existing Dimension, it is serialised correctly.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [1, 2, 3],
            "Existing Attribute": ["Provisional", "Final", "Provisional"],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "Existing Dimension",
                ExistingQbDimension(
                    "https://example.org/dimensions/existing_dimension",
                    arbitrary_rdf=[
                        TripleFragment(RDFS.label, "Existing Dimension Component")
                    ],
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#component/existing-dimension"),
        RDFS.label,
        Literal("Existing Dimension Component"),
    ) in graph


def test_arbitrary_rdf_serialisation_new_dimension():
    """
    Test that when arbitrary RDF is specified against a new dimension, it is serialised correctly.
    """
    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data(
                    "Some Dimension",
                    data["New Dimension"],
                    arbitrary_rdf=[
                        TripleFragment(RDFS.label, "New Dimension Property"),
                        TripleFragment(
                            RDFS.label,
                            "New Dimension Component",
                            RdfSerialisationHint.Component,
                        ),
                    ],
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#dimension/some-dimension"),
        RDFS.label,
        Literal("New Dimension Property"),
    ) in graph

    assert (
        URIRef("some-dataset.csv#component/some-dimension"),
        RDFS.label,
        Literal("New Dimension Component"),
    ) in graph


def test_arbitrary_rdf_serialisation_new_dimension_with_cube_uri_style_without_file_extensions():
    """
    Test that when arbitrary RDF is specified against a new dimension, it is serialised correctly.
    """
    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data(
                    "Some Dimension",
                    data["New Dimension"],
                    arbitrary_rdf=[
                        TripleFragment(RDFS.label, "New Dimension Property"),
                        TripleFragment(
                            RDFS.label,
                            "New Dimension Component",
                            RdfSerialisationHint.Component,
                        ),
                    ],
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
        uri_style=URIStyle.WithoutFileExtensions,
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset#dimension/some-dimension"),
        RDFS.label,
        Literal("New Dimension Property"),
    ) in graph

    assert (
        URIRef("some-dataset#component/some-dimension"),
        RDFS.label,
        Literal("New Dimension Component"),
    ) in graph


def test_arbitrary_rdf_serialisation_existing_dimension():
    """
    Test that when arbitrary RDF is specified against an Existing Dimension, it is serialised correctly.
    """
    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [1, 2, 3],
            "Existing Attribute": ["Provisional", "Final", "Provisional"],
        }
    )

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "Existing Dimension",
                NewQbDimension.from_data(
                    "Existing Dimension", data["Existing Dimension"]
                ),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    ExistingQbMeasure(
                        "http://some/uri/existing-measure-uri",
                        arbitrary_rdf=[
                            TripleFragment(RDFS.label, "Existing Measure Component")
                        ],
                    ),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#component/existing-measure-uri"),
        RDFS.label,
        Literal("Existing Measure Component"),
    ) in graph


def test_arbitrary_rdf_serialisation_new_measure():
    """
    Test that when arbitrary RDF is specified against a new measure, it is serialised correctly.
    """
    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("Some Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure(
                        "Some Measure",
                        arbitrary_rdf=[
                            TripleFragment(RDFS.label, "New Measure Property"),
                            TripleFragment(
                                RDFS.label,
                                "New Measure Component",
                                RdfSerialisationHint.Component,
                            ),
                        ],
                    ),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#measure/some-measure"),
        RDFS.label,
        Literal("New Measure Property"),
    ) in graph

    assert (
        URIRef("some-dataset.csv#component/some-measure"),
        RDFS.label,
        Literal("New Measure Component"),
    ) in graph


def test_qb_order_of_components():
    """
    Test that when components are created they have a qb:order value.
    """
    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})

    cube = Cube(
        CatalogMetadata("Some Dataset"),
        data,
        [
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("Some Dimension", data["New Dimension"]),
            ),
            QbColumn(
                "Value",
                QbObservationValue(
                    NewQbMeasure("Some Measure"),
                    NewQbUnit("Some Unit"),
                ),
            ),
        ],
    )

    dsd_helper = DsdToRdfModelsHelper(cube, UriHelper(cube))
    dataset = dsd_helper._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#component/some-dimension"),
        rdf.QB.order,
        Literal(1),
    ) in graph

    assert (
        URIRef("some-dataset.csv#component/measure-type"),
        rdf.QB.order,
        Literal(2),
    ) in graph

    assert (
        URIRef("some-dataset.csv#component/unit"),
        rdf.QB.order,
        Literal(3),
    ) in graph

    assert (
        URIRef("some-dataset.csv#component/some-measure"),
        rdf.QB.order,
        Literal(4),
    ) in graph


if __name__ == "__main__":
    pytest.main()
