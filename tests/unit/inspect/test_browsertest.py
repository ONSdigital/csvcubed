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


def test_pivoted_shape_csvwbrowser_and_tables():
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
    assert tables[0].csv_url == "testing-csvwbrowser-pivoted-shape.csv"
    assert tables[0].title == "Testing CsvWBrowser (pivoted shape)"
    assert tables[0].comment == "CsvWBrowser test - pivoted shape"
    assert (
        tables[0].description
        == "Testing the CsvWBrowser functionality with a pivoted shape cube generated using csvcubed"
    )

    assert tables[1].concept_scheme_uri == "local-dimension-code-list.csv#code-list"
    assert tables[1].csv_url == "local-dimension-code-list.csv"
    assert tables[1].title == "Local dimension code list"
    assert tables[1].comment == "Code list - local dimension"
    assert tables[1].description == "Code list for a locally defined dimension"


def test_pivoted_shape_data_cube_table_columns():
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
        == "local-dimension-code-list.csv#{+localdimension}"
    )
    assert (
        local_dimension_column.dimension.dimension_uri
        == "testing-csvwbrowser-pivoted-shape.csv#dimension/localdimension"
    )
    assert local_dimension_column.dimension.label == "LocalDimension"
    assert local_dimension_column.info.component.property_label == "LocalDimension"
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
    assert isinstance(external_attribute_column.attribute, ExternalAttribute)

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


if __name__ == "__main__":
    pytest.main()
