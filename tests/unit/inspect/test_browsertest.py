from pathlib import Path
from typing import OrderedDict
from unittest.mock import MagicMock, patch

import pytest
import rdflib

from csvcubed.inspect.browsercolumns import (
    AttributeColumn,
    DimensionColumn,
    MeasuresColumn,
    PivotedObservationsColumn,
    StandardShapeObservationsColumn,
    SuppressedColumn,
    UnitsColumn,
)
from csvcubed.inspect.browsercomponents import (
    ExternalAttribute,
    ExternalDimension,
    LocalAttribute,
    LocalDimension,
    LocalMeasure,
    LocalUnit,
)
from csvcubed.inspect.browsers import MetadataBrowser, TableBrowser
from csvcubed.inspect.browsertable import CodeListTable, CsvWBrowser, DataCubeTable
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodeListTableIdentifers,
    ColumnDefinition,
    CubeTableIdentifiers,
    QubeComponentResult,
)
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.data_cube_inspector import DataCubeInspector
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.utils.tableschema import CsvWRdfManager
from tests.helpers.inspectors_cache import get_csvw_rdf_manager, get_data_cube_inspector
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "inspect"


def _create_inspectors(json_path):
    graph = rdflib.ConjunctiveGraph()
    csvw_inspector = CsvWInspector(graph, json_path)
    code_list_inspector = CodeListInspector(csvw_inspector)
    data_cube_inspector = DataCubeInspector(csvw_inspector)
    return (csvw_inspector, code_list_inspector, data_cube_inspector)


def test_something():
    primary_json_file_path = (Path(".") / "some-file.json").absolute()

    (csvw_inspector, code_list_inspector, data_cube_inspector) = _create_inspectors(
        primary_json_file_path
    )

    metadata = [
        CatalogMetadataResult(
            dataset_uri="http://example.com/dataset-uri",
            graph_uri=path_to_file_uri_for_rdflib(primary_json_file_path),
            title="Some title",
            label="Some label",
            issued="1970-01-01",
            modified="2000-10-05",
            license="http://example.com/some-license",
            creator="http://example.com/some-creator",
            publisher="http://example.com/some-publisher",
            landing_pages=["http://example.com/some-landing-page"],
            themes=["http://example.com/some-theme"],
            keywords=["some keyword"],
            contact_point=["mailto:someone@example.com"],
            identifier="some-identifier",
            comment="Some comment",
            description="Some description",
        )
    ]

    anxiety_browser = CsvWBrowser(
        _test_case_base_dir / "anxiety" / "anxiety.csv-metadata.json"
    )
    anxiety_browser._csvw_inspector = csvw_inspector
    anxiety_browser._data_cube_inspector = data_cube_inspector
    anxiety_browser._code_list_inspector = code_list_inspector

    setattr(csvw_inspector, "catalog_metadata", metadata)

    setattr(
        data_cube_inspector,
        "_cube_table_identifiers",
        {
            "cube.csv": CubeTableIdentifiers(
                csv_url="cube.csv",
                data_set_url="cube.csv#dataset",
                dsd_uri="cube.csv#dsd",
            )
        },
    )
    setattr(
        code_list_inspector,
        "_code_list_table_identifiers",
        [
            CodeListTableIdentifers(
                "code-list.csv", concept_scheme_url="code-list.csv#code-list"
            )
        ],
    )

    test_metadata = anxiety_browser._csvw_inspector.get_primary_catalog_metadata()
    tables = anxiety_browser.tables
    table = tables[0]
    table_title = table.title

    assert test_metadata.title == "Some title"
    assert test_metadata.dataset_uri == "http://example.com/dataset-uri"
    assert test_metadata.graph_uri == path_to_file_uri_for_rdflib(
        primary_json_file_path
    )
    assert test_metadata.label == "Some label"
    assert test_metadata.issued == "1970-01-01"
    assert test_metadata.modified == "2000-10-05"
    assert test_metadata.license == "http://example.com/some-license"
    assert test_metadata.creator == "http://example.com/some-creator"
    assert test_metadata.publisher == "http://example.com/some-publisher"
    assert test_metadata.landing_pages == ["http://example.com/some-landing-page"]
    assert test_metadata.themes == ["http://example.com/some-theme"]
    assert test_metadata.keywords == ["some keyword"]
    assert test_metadata.contact_point == ["mailto:someone@example.com"]
    assert test_metadata.identifier == "some-identifier"
    assert test_metadata.comment == "Some comment"
    assert test_metadata.description == "Some description"
    assert len(tables) == 2


def test_pivoted_shape_csvwbrowser():
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-shape"
        / "testing-csvwbrowser-pivoted-shape.csv-metadata.json"
    )
    csvw_browser = CsvWBrowser(csvw_metadata_json_path)
    tables = csvw_browser.tables

    assert len(tables) == 2
    assert isinstance(tables[0], DataCubeTable)
    assert isinstance(tables[1], CodeListTable)

    assert tables[0].data_set_uri == "testing-csvwbrowser-pivoted-shape.csv#dataset"
    assert tables[0].shape == CubeShape.Pivoted

    assert tables[1].concept_scheme_uri == "localdimension.csv#code-list"
    assert tables[0].csv_url == "testing-csvwbrowser-pivoted-shape.csv"
    assert tables[1].csv_url == "localdimension.csv"
    assert tables[0].title == "Testing CsvWBrowser (pivoted shape)"
    assert tables[1].title == "LocalDimension"


def test_pivoted_shape_columns():
    csvw_metadata_json_path = (
        _test_case_base_dir
        / "pivoted-shape"
        / "testing-csvwbrowser-pivoted-shape.csv-metadata.json"
    )
    csvw_browser = CsvWBrowser(csvw_metadata_json_path)
    tables = csvw_browser.tables
    columns = tables[0].columns

    local_dimension_column = columns["LocalDimension"]
    assert local_dimension_column.csv_column_title == "LocalDimension"
    assert (
        local_dimension_column.cell_uri_template
        == "localdimension.csv#{+localdimension}"
    )
    assert (
        local_dimension_column.dimension.dimension_uri
        == "testing-csvwbrowser-pivoted-shape.csv#dimension/localdimension"
    )
    assert local_dimension_column.dimension.label == "LocalDimension"
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
    assert isinstance(external_dimension_column.dimension, ExternalDimension)

    local_attribute_column = columns["LocalAttribute"]
    assert local_attribute_column.csv_column_title == "LocalAttribute"
    assert local_attribute_column.cell_uri_template is None
    assert (
        local_attribute_column.attribute.attribute_uri
        == "testing-csvwbrowser-pivoted-shape.csv#attribute/localattribute"
    )
    assert local_attribute_column.attribute.label == "LocalAttribute"
    assert isinstance(local_attribute_column.attribute, LocalAttribute)

    external_attribute_column = columns["ExternalAttribute"]
    assert external_attribute_column.csv_column_title == "ExternalAttribute"
    assert (
        external_attribute_column.cell_uri_template
        == "http://www.example.org/status/{+externalattribute}"
    )
    assert (
        external_attribute_column.attribute.attribute_uri
        == "testing-csvwbrowser-pivoted-shape.csv#attribute/externalattribute"
    )
    assert external_attribute_column.attribute.label == "ExternalAttribute"
    # ExternalAttribute column being configured as LocalAttribute
    # assert isinstance(external_attribute_column.attribute, ExternalAttribute)

    pivoted_obs_column = columns["Observations"]
    assert pivoted_obs_column.csv_column_title == "Observations"
    assert pivoted_obs_column.cell_uri_template is None
    assert (
        pivoted_obs_column.unit.unit_uri
        == "testing-csvwbrowser-pivoted-shape.csv#unit/some-unit"
    )
    assert pivoted_obs_column.unit.label == "Some Unit"
    assert (
        pivoted_obs_column.measure.measure_uri
        == "testing-csvwbrowser-pivoted-shape.csv#measure/some-measure"
    )
    assert pivoted_obs_column.measure.label == "Some Measure"
    assert isinstance(pivoted_obs_column.unit, LocalUnit)
    assert isinstance(pivoted_obs_column.measure, LocalMeasure)

    # assert local_dimension_col == DimensionColumn(
    #     dimension=LocalDimension(
    #         dimension_component=local_dimension_col.info.component.component,
    #         dimension_uri="testing-csvwbrowser-pivoted-shape.csv#dimension/localdimension",
    #         label="LocalDimension",
    #     )
    # )
    # assert cols == OrderedDict(
    #     [
    #         (
    #             "LocalDimension",
    #             DimensionColumn(
    #                 dimension=LocalDimension(
    #                     dimension_uri="testing-csvwbrowser-pivoted-shape.csv#dimension/localdimension",
    #                     label="LocalDimension",
    #                 )
    #             ),
    #         ),
    #         (
    #             "ExternalDimension",
    #             DimensionColumn(
    #                 dimension=LocalDimension(
    #                     dimension_uri="http://purl.org/linked-data/sdmx/2009/dimension#refArea",
    #                     label="",
    #                 )
    #             ),
    #         ),
    #         ("SuppressedDimension", SuppressedColumn()),
    #         (
    #             "LocalAttribute",
    #             AttributeColumn(
    #                 attribute=LocalAttribute(
    #                     attribute_uri="testing-csvwbrowser-pivoted-shape.csv#attribute/localattribute",
    #                     label="LocalAttribute",
    #                 ),
    #                 required=False,
    #             ),
    #         ),
    #         (
    #             "ExternalAttribute",
    #             AttributeColumn(
    #                 attribute=LocalAttribute(
    #                     attribute_uri="testing-csvwbrowser-pivoted-shape.csv#attribute/externalattribute",
    #                     label="ExternalAttribute",
    #                 ),
    #                 required=False,
    #             ),
    #         ),
    #         (
    #             "Observations",
    #             PivotedObservationsColumn(
    #                 unit=LocalUnit(
    #                     unit_uri="testing-csvwbrowser-pivoted-shape.csv#unit/some-unit",
    #                     label="Some Unit",
    #                 ),
    #                 measure=LocalMeasure(
    #                     measure_uri="testing-csvwbrowser-pivoted-shape.csv#measure/some-measure",
    #                     label="Some Measure",
    #                 ),
    #             ),
    #         ),
    #     ]
    # )


# DimensionColumn(dimension=LocalDimension(dimension_uri='testing-csvwbrowser-pivoted-shape.csv#dimension/localdimension', label='LocalDimension'))
# DimensionColumn(dimension=LocalDimension(dimension_uri='http://purl.org/linked-data/sdmx/2009/dimension#refArea', label=''))

# def test_csvw_browser():
#     """ """
#     csvw_path = (
#         _test_case_base_dir
#         / "eurovision"
#         / "sweden-at-eurovision-complete-dataset.csv-metadata.json"
#     )

#     csv_path = (
#         _test_case_base_dir / "eurovision" / "sweden-at-eurovision-complete-dataset.csv"
#     )

#     csvw_browser = CsvWBrowser(csvw_path)
#     csvw_browser_tables = csvw_browser.tables
#     table_browser = TableBrowser(
#         csv_path, csvw_browser._data_cube_inspector, csvw_browser._code_list_inspector
#     )

#     assert len(csvw_browser_tables) == 5
#     assert csvw_browser_tables[0].csv_url == "sweden-at-eurovision-complete-dataset.csv"
#     assert csvw_browser_tables
#     assert isinstance(csvw_browser_tables[0], DataCubeTable)
#     assert isinstance(csvw_browser_tables[0].columns["Year"], DimensionColumn)
#     assert (
#         csvw_browser_tables[0].columns["Year"].dimension.dimension_uri
#         == "sweden-at-eurovision-complete-dataset.csv#dimension/year"
#     )
#     assert (
#         csvw_browser_tables[0]
#         .columns["Year"]
#         .dimension.dimension_component.property_label
#         == "Year"
#     )

#     # assert csvw_browser_tables[0].columns == OrderedDict(
#     #     [
#     #         (
#     #             "Year",
#     #             DimensionColumn(
#     #                 dimension=LocalDimension(
#     #                     dimension_uri="sweden-at-eurovision-complete-dataset.csv#dimension/year",
#     #                     label="Year",
#     #                 )
#     #             ),
#     #         ),
#     #         (
#     #             "Entrant",
#     #             DimensionColumn(
#     #                 dimension=LocalDimension(
#     #                     dimension_uri="sweden-at-eurovision-complete-dataset.csv#dimension/entrant",
#     #                     label="Entrant",
#     #                 )
#     #             ),
#     #         ),
#     #         (
#     #             "Song",
#     #             DimensionColumn(
#     #                 dimension=LocalDimension(
#     #                     dimension_uri="sweden-at-eurovision-complete-dataset.csv#dimension/song",
#     #                     label="Song",
#     #                 )
#     #             ),
#     #         ),
#     #         (
#     #             "Language",
#     #             DimensionColumn(
#     #                 dimension=LocalDimension(
#     #                     dimension_uri="sweden-at-eurovision-complete-dataset.csv#dimension/language",
#     #                     label="Language",
#     #                 )
#     #             ),
#     #         ),
#     #         (
#     #             "Value",
#     #             StandardShapeObservationsColumn(
#     #                 unit=UnitsColumn(), measures_column=MeasuresColumn()
#     #             ),
#     #         ),
#     #         ("Measure", MeasuresColumn()),
#     #         ("Unit", UnitsColumn()),
#     #         (
#     #             "Marker",
#     #             AttributeColumn(
#     #                 attribute=LocalAttribute(
#     #                     attribute_uri="sweden-at-eurovision-complete-dataset.csv#attribute/observation-status",
#     #                     label="Observation Status",
#     #                 ),
#     #                 required=False,
#     #             ),
#     #         ),
#     #     ]
#     # )

if __name__ == "__main__":
    pytest.main()
