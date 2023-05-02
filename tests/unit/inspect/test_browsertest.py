from pathlib import Path
from typing import OrderedDict
from unittest.mock import MagicMock, patch

import pytest
import rdflib

from csvcubed.inspect.browsercolumns import (
    AttributeColumn,
    DimensionColumn,
    MeasuresColumn,
    StandardShapeObservationsColumn,
    UnitsColumn,
)
from csvcubed.inspect.browsercomponents import LocalAttribute, LocalDimension
from csvcubed.inspect.browsers import MetadataBrowser, TableBrowser
from csvcubed.inspect.browsertable import CsvWBrowser, DataCubeTable
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodeListTableIdentifers,
    CubeTableIdentifiers,
)
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.sparql_handler.data_cube_inspector import DataCubeInspector
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.utils.tableschema import CsvWRdfManager
from tests.unit.test_baseunit import get_test_cases_dir

_test_case_base_dir = get_test_cases_dir() / "inspect"


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


def test_something():
    primary_json_file_path = (Path(".") / "some-file.json").absolute()
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
    graph = rdflib.ConjunctiveGraph()
    csvw_inspector = CsvWInspector(graph, primary_json_file_path)
    code_list_inspector = CodeListInspector(csvw_inspector)
    data_cube_inspector = DataCubeInspector(csvw_inspector)

    browser = CsvWBrowser(_test_case_base_dir / "anxiety" / "anxiety.csv-metadata.json")
    browser._csvw_inspector = csvw_inspector
    browser._data_cube_inspector = data_cube_inspector
    browser._code_list_inspector = code_list_inspector

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

    # metadata = browser._csvw_inspector.get_primary_catalog_metadata()
    # assert metadata.title == "Some title"

    tables = browser.tables
    assert len(tables) == 2


if __name__ == "__main__":
    pytest.main()
