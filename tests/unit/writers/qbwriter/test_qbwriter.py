from tempfile import TemporaryDirectory
import csv
from pathlib import Path

import pytest
import pandas as pd
from rdflib import RDFS, XSD, Graph, URIRef, Literal
from csvcubedmodels import rdf

from csvcubed.models.cube import *
from csvcubed.models.cube import (
    ExistingQbAttribute,
    NewQbAttribute,
    QbMultiMeasureDimension,
    QbMultiUnits,
)
from csvcubed.models.cube.uristyle import URIStyle
from csvcubed.models.cube.qb.components.arbitraryrdf import (
    TripleFragment,
    RdfSerialisationHint,
    TripleFragmentBase,
)
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.utils.iterables import first
from csvcubed.writers.qbwriter import QbWriter
from csvcubed.writers.helpers.skoscodelistwriter.constants import SCHEMA_URI_IDENTIFIER


@dataclass
class TestQbMeasure(QbMeasure, UriIdentifiable):
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        pass

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        pass

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        pass

    def get_identifier(self) -> str:
        pass


empty_cube = Cube(CatalogMetadata("Cube Name"), pd.DataFrame, [])
empty_qbwriter = QbWriter(empty_cube)


def test_output_new_code_list_csvws_urls():
    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})
    cube = Cube(
        CatalogMetadata("Cube Name"),
        pd.DataFrame(),
        [
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("Some Dimension", data["New Dimension"]),
            )
        ],
    )
    qb_writer = QbWriter(cube)
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        qb_writer._output_new_code_list_csvws(temp_dir)
        graph = Graph()
        graph.parse(
            temp_dir / "some-dimension.csv-metadata.json", publicID="file://relative/"
        )
        assert (
            URIRef(f"file://relative/some-dimension.csv#code-list"),
            URIRef("http://www.w3.org/ns/csvw#url"),
            Literal("some-dimension.csv", datatype=XSD.anyURI),
        ) in graph


def test_output_new_code_list_csvws_urls_with_uri_style_without_file_extensions():
    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, 2, 3]})
    cube = Cube(
        CatalogMetadata("Cube Name"),
        pd.DataFrame(),
        [
            QbColumn(
                "New Dimension",
                NewQbDimension.from_data("Some Dimension", data["New Dimension"]),
            )
        ],
        uri_style=URIStyle.WithoutFileExtensions,
    )
    qb_writer = QbWriter(cube)
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        qb_writer._output_new_code_list_csvws(temp_dir)
        graph = Graph()
        graph.parse(
            temp_dir / "some-dimension.csv-metadata.json", publicID="file://relative/"
        )
        assert (
            URIRef(f"file://relative/some-dimension#code-list"),
            URIRef("http://www.w3.org/ns/csvw#url"),
            Literal("some-dimension.csv", datatype=XSD.anyURI),
        ) in graph


def test_csv_col_definition_default_property_value_urls():
    """
    When configuring a CSV-W column definition, if the user has not specified an `csv_column_uri_template`
    against the `QbColumn` then the `propertyUrl` and `valueUrl`s should both be populated by the default
    values inferred from the component.
    """
    column = QbColumn("Some Column", QbMultiUnits([NewQbUnit("Some Unit")]))
    csv_col = empty_qbwriter._generate_csvw_column_definition(column)
    assert (
        "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
        == csv_col["propertyUrl"]
    )
    assert "cube-name.csv#unit/{+some_column}" == csv_col["valueUrl"]


def test_csv_col_definition_csv_column_uri_template_override():
    """
    When configuring a CSV-W column definition, if the user has specified an `csv_column_uri_template` against the
    `QbColumn` then this should end up as the resulting CSV-W column's `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        ExistingQbDimension("http://base-uri/dimensions/some-dimension"),
        csv_column_uri_template="http://base-uri/some-alternative-output-uri/{+some_column}",
    )
    csv_col = empty_qbwriter._generate_csvw_column_definition(column)
    assert "http://base-uri/dimensions/some-dimension" == csv_col["propertyUrl"]
    assert (
        "http://base-uri/some-alternative-output-uri/{+some_column}"
        == csv_col["valueUrl"]
    )


def test_csv_col_definition():
    """
    Test basic configuration of a CSV-W column definition.
    """
    column = QbColumn(
        "Some Column",
        ExistingQbDimension("http://base-uri/dimensions/some-dimension"),
    )
    csv_col = empty_qbwriter._generate_csvw_column_definition(column)
    assert "suppressOutput" not in csv_col
    assert csv_col["titles"] == "Some Column"
    assert csv_col["name"] == "some_column"
    assert csv_col["propertyUrl"] == "http://base-uri/dimensions/some-dimension"
    assert csv_col["valueUrl"] == "{+some_column}"
    assert csv_col["required"]


def test_csv_col_required():
    """Test that the :attr:`required` key is set correctly for various different component types."""
    required_columns = [
        QbColumn(
            "Some Dimension",
            ExistingQbDimension("http://base-uri/dimensions/some-dimension"),
        ),
        QbColumn(
            "Some Required Attribute",
            NewQbAttribute("Some Attribute", is_required=True),
        ),
        QbColumn("Some Multi Units", QbMultiUnits([])),
        QbColumn("Some Measure Dimension", QbMultiMeasureDimension([])),
        QbColumn(
            "Some Obs Val",
            QbObservationValue(NewQbMeasure("Some Measure")),
        ),
    ]

    optional_columns = [
        QbColumn(
            "Some Optional Attribute",
            NewQbAttribute("Some Attribute", is_required=False),
        )
    ]

    for col in required_columns:
        csv_col = empty_qbwriter._generate_csvw_column_definition(col)
        required = csv_col["required"]
        assert isinstance(required, bool)
        assert required

    for col in optional_columns:
        csv_col = empty_qbwriter._generate_csvw_column_definition(col)
        required = csv_col["required"]
        assert isinstance(required, bool)
        assert not required


def test_csv_col_required_observed_value_with_obs_status_attribute():
    """Test that the observation value column is **not** marked as `required` in the CSV-W where an `sdmxa:obsStatus`
    attribute column is defined in the same cube."""
    observed_values_column = QbColumn(
        "Values",
        QbObservationValue(
            NewQbMeasure("Some Measure"),
            NewQbUnit("Some Unit"),
        ),
    )

    qube = Cube(
        metadata=CatalogMetadata("Some Qube"),
        data=None,
        columns=[
            QbColumn("Some Dimension", NewQbDimension(label="Some Dimension")),
            observed_values_column,
            QbColumn(
                "Marker",
                ExistingQbAttribute(
                    "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
                ),
                csv_column_uri_template="https://example.org/some_attribute/{+Some_attribute}",
            ),
        ],
    )
    writer = QbWriter(qube)
    observed_values_column_is_required = writer._generate_csvw_column_definition(
        observed_values_column
    )["required"]
    assert isinstance(observed_values_column_is_required, bool)
    assert not observed_values_column_is_required


def test_csv_col_definition_suppressed():
    """
    Test basic configuration of a *suppressed* CSV-W column definition.
    """
    column = SuppressedCsvColumn("Some Column")
    csv_col = empty_qbwriter._generate_csvw_column_definition(column)
    assert csv_col["suppressOutput"]
    assert "Some Column" == csv_col["titles"]
    assert "some_column" == csv_col["name"]
    assert "propertyUrl" not in csv_col
    assert "valueUrl" not in csv_col


def test_virtual_columns_generated_for_single_obs_val():
    """
    Ensure that the virtual columns generated for a `QbObservationValue`'s unit and measure are correct.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", NewQbDimension("Some Dimension")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )
    writer = QbWriter(cube)

    virtual_columns = (
        writer._generate_virtual_columns_for_obs_vals_in_pivoted_shape_cube()
    )

    virt_col = first(virtual_columns, lambda x: x["name"] == "virt_slice")
    assert virt_col is not None
    assert virt_col["virtual"] == True
    assert virt_col["propertyUrl"] == "rdf:type"
    assert virt_col["valueUrl"] == "qb:Slice"

    virt_col = first(virtual_columns, lambda x: x["name"] == "virt_obs_some_obs_val")
    assert virt_col is not None
    assert virt_col["virtual"] == True
    assert virt_col["propertyUrl"] == "qb:Observation"
    assert virt_col["valueUrl"] == "cube.csv#obs/{some_dimension}@some-measure"

    virt_col = first(
        virtual_columns, lambda x: x["name"] == "virt_obs_some_obs_val_meas"
    )
    assert virt_col is not None
    assert virt_col["virtual"] == True
    assert virt_col["aboutUrl"] == "cube.csv#obs/{some_dimension}@some-measure"
    assert virt_col["propertyUrl"] == "qb:measureType"
    assert virt_col["valueUrl"] == "cube.csv#measure/some-measure"

    virt_col = first(
        virtual_columns, lambda x: x["name"] == "virt_dim_some_obs_val_some_dimension"
    )
    assert virt_col is not None
    assert virt_col["virtual"] == True
    assert virt_col["aboutUrl"] == "cube.csv#obs/{some_dimension}@some-measure"
    assert virt_col["propertyUrl"] == "cube.csv#dimension/some-dimension"
    assert virt_col["valueUrl"] == "{+some_dimension}"

    virt_col = first(
        virtual_columns, lambda x: x["name"] == "virt_obs_some_obs_val_type"
    )
    assert virt_col is not None
    assert virt_col["virtual"] == True
    assert virt_col["aboutUrl"] == "cube.csv#obs/{some_dimension}@some-measure"
    assert virt_col["propertyUrl"] == "rdf:type"
    assert virt_col["valueUrl"] == "qb:Observation"

    virt_col = first(
        virtual_columns, lambda x: x["name"] == "virt_dataSet_some_obs_val"
    )
    assert virt_col is not None
    assert virt_col["virtual"] == True
    assert virt_col["aboutUrl"] == "cube.csv#obs/{some_dimension}@some-measure"
    assert virt_col["propertyUrl"] == "qb:dataSet"
    assert virt_col["valueUrl"] == "cube.csv#dataset"


def test_virtual_columns_generated_for_multi_meas_obs_val():
    """
    Ensure that the virtual column generated for a `QbObservationValue`'s unit and measure are
    correct.
    """
    obs_val = QbObservationValue(unit=NewQbUnit("Some Unit"))
    virtual_columns = (
        empty_qbwriter._generate_virtual_columns_for_obs_val_in_standard_shape_cube(
            obs_val
        )
    )

    virt_unit = first(virtual_columns, lambda x: x["name"] == "virt_unit")
    assert virt_unit is not None
    assert virt_unit["virtual"]
    assert (
        "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
        == virt_unit["propertyUrl"]
    )
    assert "cube-name.csv#unit/some-unit" == virt_unit["valueUrl"]


def test_serialise_new_attribute_values():
    """
    When new attribute values are serialised, a list of new metadata resources should be returned.
    """

    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [2, 2, 2],
            "New Attribute": ["Pending", "Final", "In Review"],
            "Existing Attribute": ["D", "E", "F"],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Existing Dimension",
            ExistingQbDimension("https://example.org/dimensions/existing_dimension"),
        ),
        QbColumn(
            "Value",
            QbObservationValue(
                ExistingQbMeasure("http://example.org/existing/measure"),
                ExistingQbUnit("http://example.org/some/existing/unit"),
            ),
        ),
        QbColumn(
            "New Attribute",
            NewQbAttribute.from_data("New Attribute", data["New Attribute"]),
        ),
        QbColumn(
            "Existing Attribute",
            ExistingQbAttribute(
                "http://example.org/some/existing/attribute",
                new_attribute_values=[
                    NewQbAttributeValue(
                        "D",
                        description="real value",
                        parent_attribute_value_uri="http://parent-uri",
                    ),
                    NewQbAttributeValue("E", source_uri="http://source-uri"),
                    NewQbAttributeValue("F"),
                ],
            ),
        ),
    ]

    cube = Cube(metadata, data, columns)

    qbwriter = QbWriter(cube)
    list_of_new_attribute_values = qbwriter._get_new_attribute_value_resources()

    map_label_to_expected_config = {
        "Pending": {
            "uri": "some-dataset.csv#attribute/new-attribute/pending",
            "description": None,
            "parent_attribute_value_uri": None,
            "source_uri": None,
        },
        "Final": {
            "uri": "some-dataset.csv#attribute/new-attribute/final",
            "description": None,
            "parent_attribute_value_uri": None,
            "source_uri": None,
        },
        "In Review": {
            "uri": "some-dataset.csv#attribute/new-attribute/in-review",
            "description": None,
            "parent_attribute_value_uri": None,
            "source_uri": None,
        },
        "D": {
            "uri": "some-dataset.csv#attribute/existing-attribute/d",
            "description": "real value",
            "parent_attribute_value_uri": "http://parent-uri",
            "source_uri": None,
        },
        "E": {
            "uri": "some-dataset.csv#attribute/existing-attribute/e",
            "description": None,
            "parent_attribute_value_uri": None,
            "source_uri": "http://source-uri",
        },
        "F": {
            "uri": "some-dataset.csv#attribute/existing-attribute/f",
            "description": None,
            "parent_attribute_value_uri": None,
            "source_uri": None,
        },
    }

    for (label, expected_config) in map_label_to_expected_config.items():
        new_attribute_value = first(
            list_of_new_attribute_values, lambda x: x.label == label
        )
        assert new_attribute_value is not None
        assert new_attribute_value.uri_str == expected_config["uri"]
        assert new_attribute_value.comment == expected_config["description"]

        assert (
            expected_config["parent_attribute_value_uri"] is None
            and new_attribute_value.parent_attribute_value_uri is None
        ) or str(new_attribute_value.parent_attribute_value_uri.uri) == expected_config[
            "parent_attribute_value_uri"
        ]

        assert (
            expected_config["source_uri"] is None
            and new_attribute_value.source_uri is None
        ) or str(new_attribute_value.source_uri.uri) == expected_config["source_uri"]


def test_serialise_unit():
    """
    When new units are serialised, a list of new metadata resources should be returned.
    """

    data = pd.DataFrame(
        {
            "Existing Dimension": ["A", "B", "C"],
            "Value": [2, 2, 2],
            "Units": ["Percent", "People", "People"],
        }
    )

    metadata = CatalogMetadata("Some Dataset")
    columns = [
        QbColumn(
            "Existing Dimension",
            ExistingQbDimension("https://example.org/dimensions/existing_dimension"),
        ),
        QbColumn(
            "Value",
            QbObservationValue(
                ExistingQbMeasure("http://example.org/existing/measure")
            ),
        ),
        QbColumn(
            "Units",
            QbMultiUnits(
                [
                    NewQbUnit(
                        "Percent",
                        description="unit",
                        base_unit=ExistingQbUnit("http://parent-uri"),
                    ),
                    NewQbUnit(
                        "People",
                        source_uri="http://source-uri",
                        si_base_unit_conversion_multiplier=25.1364568,
                        qudt_quantity_kind_uri="http://some-quantity-kind-family",
                    ),
                ],
            ),
        ),
    ]

    cube = Cube(metadata, data, columns)

    qbwriter = QbWriter(cube)
    list_of_new_unit_resources = qbwriter._get_new_unit_resources()

    map_label_to_expected_config = {
        "Percent": {
            "uri": "some-dataset.csv#unit/percent",
            "description": "unit",
            "parent_unit_uri": "http://parent-uri",
            "source_uri": None,
            "qudt_quantity_kind_family": None,
            "qudt_conversion_multiplier": None,
        },
        "People": {
            "uri": "some-dataset.csv#unit/people",
            "description": None,
            "parent_unit_uri": None,
            "source_uri": "http://source-uri",
            "qudt_quantity_kind_family": "http://some-quantity-kind-family",
            "qudt_conversion_multiplier": 25.1364568,
        },
    }
    for (label, expected_config) in map_label_to_expected_config.items():
        new_attribute_value = first(
            list_of_new_unit_resources, lambda x: x.label == label
        )
        assert new_attribute_value is not None
        assert new_attribute_value.uri_str == expected_config["uri"]
        assert new_attribute_value.comment == expected_config["description"]
        assert (
            expected_config["source_uri"] is None
            and new_attribute_value.source_uri is None
        ) or str(new_attribute_value.source_uri.uri) == expected_config["source_uri"]
        assert (
            expected_config["parent_unit_uri"] is None
            and new_attribute_value.base_unit_uri is None
        ) or str(new_attribute_value.base_unit_uri.uri) == expected_config[
            "parent_unit_uri"
        ]

        assert (
            expected_config["qudt_conversion_multiplier"] is None
            and new_attribute_value.qudt_conversion_multiplier is None
        ) or new_attribute_value.qudt_conversion_multiplier == expected_config[
            "qudt_conversion_multiplier"
        ]
        assert (
            expected_config["qudt_quantity_kind_family"] is None
            and new_attribute_value.has_qudt_quantity_kind is None
        ) or str(new_attribute_value.has_qudt_quantity_kind.uri) == expected_config[
            "qudt_quantity_kind_family"
        ]


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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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


def test_arbitrary_rdf_serialisation_new_dimension_with_cube_uri_style_WithoutFileExtensions():
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
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

    qb_writer = QbWriter(cube)
    dataset = qb_writer._generate_qb_dataset_dsd_definitions()
    graph = dataset.to_graph(Graph())

    assert (
        URIRef("some-dataset.csv#component/some-dimension"),
        rdf.QB.order,
        Literal(1),
    ) in graph

    assert (URIRef("some-dataset.csv#component/measure-type"), rdf.QB.order, Literal(2))

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


def test_output_integer_obs_val_with_missing_values():
    """
    Due to the way that pandas represents missing values (as NaN), instead of interpreting an integer data column as
     integers, it represents the column as decimal values when some values are missing. Therefore we need to explicitly
     coerce these values back to integers.

     This test ensures that we can write CSVs to disk which contain integer values even when one of the obs_vals is
     missing.
    """

    data = pd.DataFrame({"New Dimension": ["A", "B", "C"], "Value": [1, None, 3]})

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
                    data_type="int",
                ),
            ),
        ],
    )

    qb_writer = QbWriter(cube)
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        qb_writer.write(temp_dir)
        with open(temp_dir / "some-dataset.csv") as csv_file:
            rows = list(csv.reader(csv_file, delimiter=",", quotechar='"'))
            for row in rows[1:]:
                value: str = row[1]
                if len(value) > 0:
                    # If any of the values are not integers (e.g. "1.0") the next line will throw an exception.
                    int_val = int(value)
                    assert isinstance(int_val, int)
                # else: len == 0 implies it's a missing value, which is expected in one location.


if __name__ == "__main__":
    pytest.main()
