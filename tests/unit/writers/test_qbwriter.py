from ast import Pass
from tempfile import TemporaryDirectory
from typing import List
from copy import deepcopy
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
from csvcubed.writers.urihelpers.skoscodelistconstants import SCHEMA_URI_IDENTIFIER


@dataclass
class TestQbMeasure(QbMeasure, UriIdentifiable):
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def _get_arbitrary_rdf(self) -> List[TripleFragmentBase]:
        pass

    def _get_identifiable_state(self) -> tuple:
        pass

    def __eq__(self, _):
        Pass

    def __hash__(self):
        pass

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        pass

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        pass

    def get_identifier(self) -> str:
        pass


def _get_standard_cube_for_columns(columns: List[CsvColumn]) -> Cube:
    data = pd.DataFrame(
        {
            "Country": ["Wales", "Scotland", "England", "Northern Ireland"],
            "Observed Value": [101.5, 56.2, 12.4, 77.8],
            "Marker": ["Provisional", "Provisional", "Provisional", "Provisional"],
        }
    )
    metadata: CatalogMetadata = CatalogMetadata("Cube Name")

    return Cube(deepcopy(metadata), data.copy(deep=True), columns)


def _assert_component_defined(
    dataset: rdf.qb.DataSet, name: str
) -> rdf.qb.ComponentSpecification:
    component = first(
        dataset.structure.components,
        lambda x: str(x.uri) == f"cube-name.csv#component/{name}",
    )
    assert component is not None
    return component


def _assert_component_property_defined(
    component: rdf.qb.ComponentSpecification, property_uri: str
) -> None:
    property = first(
        component.componentProperties, lambda x: str(x.uri) == property_uri
    )
    assert property is not None
    return property


empty_cube = Cube(CatalogMetadata("Cube Name"), pd.DataFrame, [])
empty_qbwriter = QbWriter(empty_cube)


def test_structure_defined():
    cube = _get_standard_cube_for_columns(
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

    qbwriter = QbWriter(cube)
    dataset = qbwriter._generate_qb_dataset_dsd_definitions()

    assert dataset is not None

    assert dataset.structure is not None
    assert type(dataset.structure) == rdf.qb.DataStructureDefinition

    assert dataset.structure.componentProperties is not None

    _assert_component_defined(dataset, "country")
    _assert_component_defined(dataset, "marker")
    _assert_component_defined(dataset, "unit")
    _assert_component_defined(dataset, "some-existing-measure")


def test_structure_uri():
    cube = Cube(CatalogMetadata("Cube Name"))
    qbwriter = QbWriter(cube)

    actual = qbwriter._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name.csv#")


def test_structure_uri_standard_pattern():
    cube = Cube(CatalogMetadata("Cube Name"), uri_style=URIStyle.Standard)
    qbwriter = QbWriter(cube)

    actual = qbwriter._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name.csv#")


def test_structure_uri_withoutFileExtensions_pattern():
    cube = Cube(CatalogMetadata("Cube Name"), uri_style=URIStyle.WithoutFileExtensions)
    qbwriter = QbWriter(cube)

    actual = qbwriter._generate_qb_dataset_dsd_definitions().structure.uri_str
    assert actual.startswith("cube-name#")


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
        empty_qbwriter._get_default_value_uri_for_code_list_concepts(column, code_list)
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
        empty_qbwriter._get_default_value_uri_for_code_list_concepts(column, code_list)
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
        empty_qbwriter._get_default_value_uri_for_code_list_concepts(column, code_list)
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
        empty_qbwriter._get_default_value_uri_for_code_list_concepts(column, code_list)
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
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
    uri_styled_qbwriter = QbWriter(uri_styled_cube)

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
    ) = uri_styled_qbwriter._get_default_property_value_uris_for_column(column)
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert "http://base-uri/attributes/existing-attribute" == default_property_uri
    assert "{+some_column}" == default_value_uri


def test_default_property_value_uris_existing_attribute_new_values():
    """
    When an existing attribute is used, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn(
        "Some Column",
        ExistingQbAttribute(
            "http://base-uri/attributes/existing-attribute",
            new_attribute_values=[NewQbAttributeValue("Some Attribute Value")],
        ),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert "http://base-uri/attributes/existing-attribute" == default_property_uri
    assert "cube-name.csv#attribute/some-column/{+some_column}" == default_value_uri


def test_default_property_value_uris_new_attribute_existing_values():
    """
    When a new attribute is defined, we can provide the `propertyUrl`, but we cannot guess the `valueUrl`.
    """
    column = QbColumn("Some Column", NewQbAttribute("This New Attribute"))
    (
        default_property_uri,
        default_value_uri,
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
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
            new_attribute_values=[NewQbAttributeValue("Something")],
        ),
    )
    (
        default_property_uri,
        default_value_uri,
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert (
        "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
        == default_property_uri
    )
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert (
        "http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"
        == default_property_uri
    )
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
            empty_qbwriter._get_default_property_value_uris_for_column(column)

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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert "http://purl.org/linked-data/cube#measureType" == default_property_uri
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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert "http://purl.org/linked-data/cube#measureType" == default_property_uri
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
            empty_qbwriter._get_default_property_value_uris_for_column(column)

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
    ) = empty_qbwriter._get_default_property_value_uris_for_column(column)
    assert default_property_uri == "cube-name.csv#measure/new-qb-measure"
    assert default_value_uri is None


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


def test_output_new_code_list_csvws_urls_with_uri_style_WithoutFileExtensions():
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
    writer = QbWriter(cube)

    (
        default_property_uri,
        default_value_uri,
    ) = writer._get_default_property_value_uris_for_column(column)
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
    writer = QbWriter(cube)

    (
        default_property_uri,
        default_value_uri,
    ) = writer._get_default_property_value_uris_for_column(column)
    assert default_property_uri == "http://some-existing-measures/{+measure}"
    assert default_value_uri is None


def test_csv_col_definition_default_property_value_urls():
    """
    When configuring a CSV-W column definition, if the user has not specified an `csv_column_uri_template`
    against the `QbColumn` then the `propertyUrl` and `valueUrl`s should both be populated by the default
    values inferred from the component.
    """
    column = QbColumn("Some Column", QbMultiUnits([NewQbUnit("Some Unit")]))
    csv_col = empty_qbwriter._generate_csvqb_column(column)
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
    csv_col = empty_qbwriter._generate_csvqb_column(column)
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
    csv_col = empty_qbwriter._generate_csvqb_column(column)
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
        csv_col = empty_qbwriter._generate_csvqb_column(col)
        required = csv_col["required"]
        assert isinstance(required, bool)
        assert required

    for col in optional_columns:
        csv_col = empty_qbwriter._generate_csvqb_column(col)
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
    observed_values_column_is_required = writer._generate_csvqb_column(
        observed_values_column
    )["required"]
    assert isinstance(observed_values_column_is_required, bool)
    assert not observed_values_column_is_required


def test_csv_col_definition_suppressed():
    """
    Test basic configuration of a *suppressed* CSV-W column definition.
    """
    column = SuppressedCsvColumn("Some Column")
    csv_col = empty_qbwriter._generate_csvqb_column(column)
    assert csv_col["suppressOutput"]
    assert "Some Column" == csv_col["titles"]
    assert "some_column" == csv_col["name"]
    assert "propertyUrl" not in csv_col
    assert "valueUrl" not in csv_col


def test_get_observation_value_col_for_column():
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

    writer = QbWriter(cube)
    actual_obs_val_col = writer._get_observation_value_col_for_column("Some Obs Val")

    assert actual_obs_val_col == expected_obs_val_col


def test_get_observation_value_col_for_column_when_col_title_is_invalid():
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

    writer = QbWriter(cube)
    with pytest.raises(Exception) as err:
        writer._get_observation_value_col_for_column("Invalid Col Title")

    assert (
        str(err.value)
        == 'Could not find one observation value column. Found 0 for title: "Invalid Col Title".'
    )


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
    writer = QbWriter(cube)

    actual_slice_key = writer._get_cross_measures_slice_key()
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
            QbColumn("Some Dimension", ExistingQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )
    writer = QbWriter(cube)

    actual_slice_key = writer._get_cross_measures_slice_key()
    assert str(actual_slice_key.uri) == "cube.csv#slice/cross-measures"

    component_properties = list(actual_slice_key.componentProperties)
    assert len(component_properties) == 1
    assert str(component_properties[0].uri) == "Some Dimension"


def test_is_cube_in_pivoted_shape_true():
    """
    Ensure that the boolean returned for an input cube of pivoted shape is true.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", ExistingQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn(
                "Some Obs Val",
                QbObservationValue(
                    NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
                ),
            ),
        ],
    )

    writer = QbWriter(cube)
    is_cube_pivoted = writer.is_cube_in_pivoted_shape
    assert is_cube_pivoted == True


# TODO: CHECK WITH ROB
def test_is_cube_in_pivoted_shape_false():
    """
    Ensure that the boolean returned for an input cube of pivoted shape is false.
    """
    cube = Cube(
        CatalogMetadata("Cube"),
        columns=[
            QbColumn("Some Dimension", ExistingQbDimension("Some Dimension")),
            QbColumn("Some Attribute", NewQbAttribute(label="Some Attribute")),
            QbColumn("Some Obs Val", QbObservationValue(NewQbUnit("Some Unit"))),
        ],
    )

    writer = QbWriter(cube)
    is_cube_pivoted = writer.is_cube_in_pivoted_shape
    assert is_cube_pivoted == False


# TODO: CHECK WITH ROB
def test_is_cube_in_pivoted_shape_raise_exception():
    pass


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

    writer = QbWriter(cube)
    actual_observation_uri = writer._get_observation_uri_for_pivoted_shape_data_set(
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

    writer = QbWriter(cube)
    actual_observation_uri = writer._get_observation_uri_for_pivoted_shape_data_set(
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

    writer = QbWriter(cube)
    with pytest.raises(Exception) as exception:
        writer._get_observation_uri_for_pivoted_shape_data_set(obs_val_column)
        assert (
            str(exception.value) == f"Unhandled QbMeasure type {type(obs_val_measure)}"
        )


def test_get_pivoted_cube_slice_uri():
    """
    Ensures that the pivoted shape cube slice URI is returned.
    """
    pass


def test_get_about_url():
    """
    Ensures that the pivotes shape cube about URL is returned.
    """
    pass


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
        writer._generate_virtual_columns_for_obs_val_in_pivoted_shape_cube()
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

    actual_about_url = QbWriter(cube)._get_about_url()
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

    actual_about_url = QbWriter(cube)._get_about_url()
    expected_about_url = "some-dataset.csv#slice/{existing_dimension},{local_dimension}"
    assert actual_about_url == expected_about_url


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
