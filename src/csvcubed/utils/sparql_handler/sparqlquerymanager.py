"""
SPARQL Queries
----------------------

Collection of SPARQL queries.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List

import rdflib
from csvcubedmodels.rdf.namespaces import XSD
from rdflib import Literal, URIRef
from rdflib.query import ResultRow

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.models.csvcubedexception import (
    FailedToReadSparqlQueryException,
    InvalidNumberOfRecordsException,
)
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparql.valuesbinding import ValuesBinding
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodelistsResult,
    ColumnDefinition,
    CSVWTableSchemaFileDependenciesResult,
    CubeTableIdentifiers,
    IsPivotedShapeMeasureResult,
    MetadataDependenciesResult,
    PrimaryKeyColNamesByDatasetUrlResult,
    QubeComponentsResult,
    TableSchemaPropertiesResult,
    UnitResult,
    map_catalog_metadata_results,
    map_codelists_sparql_result,
    map_column_definition_results,
    map_csvw_table_schemas_file_dependencies_result,
    map_data_set_dsd_csv_url_result,
    map_is_pivoted_shape_for_measures_in_data_set,
    map_labels_for_resource_uris,
    map_metadata_dependency_results,
    map_primary_key_col_names_by_csv_url_result,
    map_qube_components_sparql_result,
    map_table_schema_properties_results,
    map_units,
)
from csvcubed.utils.sparql_handler.sparql import ask, select

_logger = logging.getLogger(__name__)


class SPARQLQueryName(Enum):
    """
    The names of sparql queries.
    """

    ASK_IS_CODELIST = "ask_is_codelist"

    ASK_IS_QB_DATASET = "ask_is_qb_dataset"

    SELECT_CATALOG_METADATA = "select_catalog_metadata"

    SELECT_DATA_SET_DSD_CSV_URL = "select_data_set_dsd_csv_url"

    SELECT_DSD_QUBE_COMPONENTS = "select_dsd_qube_components"

    SELECT_CODELISTS_AND_COLS = "select_codelists_and_cols"

    SELECT_UNITS = "select_units"

    SELECT_CSVW_TABLE_SCHEMA_FILE_DEPENDENCIES = (
        "select_csvw_table_schema_file_dependencies"
    )

    SELECT_CODELIST_COLS_BY_CSV_URL = "select_codelist_cols_by_csv_url"

    SELECT_CODELIST_PRIMARY_KEY_BY_CSV_URL = "select_codelist_primary_key_by_csv_url"

    SELECT_METADATA_DEPENDENCIES = "select_metadata_dependencies"

    SELECT_TABLE_SCHEMA_PROPERTIES = "select_table_schema_properties"

    SELECT_IS_PIVOTED_SHAPE_FOR_MEASURES_IN_DATA_SET = (
        "select_is_pivoted_shape_for_measures_in_data_set"
    )

    SELECT_COLUMN_DEFINITIONS = "select_column_definitions"

    SELECT_LABELS_FOR_RESOURCE_URIS = "select_labels_for_resource_uris"


def _get_query_string_from_file(query_type: SPARQLQueryName) -> str:
    """
    Read the sparql query string from sparql file for the given query type.

    Member of :file:`./sparqlquerymanager.py`

    :return: `str` - String containing the sparql query.
    """
    _logger.debug(f"Root path: {APP_ROOT_DIR_PATH.absolute()}")

    file_path: Path = (
        APP_ROOT_DIR_PATH
        / "utils"
        / "sparql_handler"
        / "sparql_queries"
        / (query_type.value + ".sparql")
    )
    _logger.debug(f"{query_type.value} query file path: {file_path.absolute()}")

    try:
        with open(
            file_path,
            "r",
        ) as f:
            return f.read()
    except Exception as ex:
        raise FailedToReadSparqlQueryException(
            sparql_file_path=file_path.absolute()
        ) from ex


def ask_is_csvw_code_list(rdf_graph: rdflib.Graph) -> bool:
    """
    Queries whether the given rdf is a code list (i.e. skos:ConceptScheme).

    Member of :file:`./sparqlquerymanager.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        SPARQLQueryName.ASK_IS_QB_DATASET.ASK_IS_CODELIST.value,
        _get_query_string_from_file(SPARQLQueryName.ASK_IS_CODELIST),
        rdf_graph,
    )


def ask_is_csvw_qb_dataset(rdf_graph: rdflib.Graph) -> bool:
    """
    Queries whether the given rdf is a qb dataset (i.e. qb:Dataset).

    Member of :file:`./sparqlquerymanager.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        SPARQLQueryName.ASK_IS_QB_DATASET.ASK_IS_QB_DATASET.value,
        _get_query_string_from_file(SPARQLQueryName.ASK_IS_QB_DATASET),
        rdf_graph,
    )


def select_csvw_catalog_metadata(
    rdf_graph: rdflib.Graph,
) -> List[CatalogMetadataResult]:
    """
    Queries catalog metadata such as title, label, issued date/time, modified data/time, etc.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CatalogMetadataResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_CATALOG_METADATA),
        rdf_graph,
    )

    return map_catalog_metadata_results(results)


def select_data_set_dsd_and_csv_url(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> List[CubeTableIdentifiers]:
    """
    Selects the dataset's DSD and CSV URL. Returns a list of cube table identifiers containing the results.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_DATA_SET_DSD_CSV_URL),
        rdf_graph,
    )

    if len(results) == 0:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_DATA_SET_DSD_CSV_URL.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )
    return map_data_set_dsd_csv_url_result(results)


def select_csvw_dsd_qube_components(
    rdf_graph: rdflib.ConjunctiveGraph,
    json_path: Path,
    map_dsd_uri_to_csv_url: Dict[str, str],
    map_csv_url_to_column_definitions: Dict[str, List[ColumnDefinition]],
    map_csv_url_to_cube_shape: Dict[str, CubeShape],
) -> Dict[str, QubeComponentsResult]:
    """
    Queries the list of qube components.

    Returns a map of csv_url to the `QubeComponentsResult`.

    Member of :file:`./sparqlquerymanager.py`

    :return: `Dict[str, QubeComponentsResult]`
    """
    result_dsd_components: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_DSD_QUBE_COMPONENTS),
        rdf_graph,
    )

    return map_qube_components_sparql_result(
        result_dsd_components,
        json_path,
        map_dsd_uri_to_csv_url,
        map_csv_url_to_column_definitions,
        map_csv_url_to_cube_shape,
    )


def select_is_pivoted_shape_for_measures_in_data_set(
    rdf_graph: rdflib.ConjunctiveGraph,
    cube_table_identifiers: List[CubeTableIdentifiers],
) -> List[IsPivotedShapeMeasureResult]:
    """
    Queries the measure and whether it is a part of a pivoted or standard shape cube.
    """
    result_is_pivoted_shape: List[ResultRow] = select(
        _get_query_string_from_file(
            SPARQLQueryName.SELECT_IS_PIVOTED_SHAPE_FOR_MEASURES_IN_DATA_SET
        ),
        rdf_graph,
        values_bindings=[
            _cube_table_identifiers_to_values_binding(cube_table_identifiers)
        ],
    )

    return map_is_pivoted_shape_for_measures_in_data_set(result_is_pivoted_shape)


def _cube_table_identifiers_to_values_binding(
    csv_dsd_dataset_uris: List[CubeTableIdentifiers],
) -> ValuesBinding:
    return ValuesBinding(
        variable_names=["csvUrl", "dataSet", "dsd"],
        rows=[
            [
                Literal(uris.csv_url, datatype=XSD.anyURI),
                URIRef(uris.data_set_url),
                URIRef(uris.dsd_uri),
            ]
            for uris in csv_dsd_dataset_uris
        ],
    )


def _uris_to_values_binding(uris: List[str]) -> ValuesBinding:
    return ValuesBinding(
        variable_names=["resourceValUri"], rows=[[URIRef(uri)] for uri in uris]
    )


def select_labels_for_resource_uris(
    rdf_graph: rdflib.ConjunctiveGraph, resource_uris: List[str]
) -> Dict[str, str]:
    """
    Queries a list of value uris and returns associated labels

    Member of :file:`./sparqlquerymanager.py`

    :return: `Dict[str, str]`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_LABELS_FOR_RESOURCE_URIS),
        rdf_graph,
        values_bindings=[_uris_to_values_binding(resource_uris)],
    )

    return map_labels_for_resource_uris(results)


def select_dsd_code_list_and_cols(
    rdf_graph: rdflib.ConjunctiveGraph,
    json_path: Path,
) -> Dict[str, CodelistsResult]:
    """
    Queries code lists and columns in the data cube.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CodelistInfoSparqlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_CODELISTS_AND_COLS),
        rdf_graph,
    )
    return map_codelists_sparql_result(results, json_path)


def select_csvw_table_schema_file_dependencies(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> CSVWTableSchemaFileDependenciesResult:
    """
    Queries the table schemas of the given csvw json-ld.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CSVWTabelSchemasResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(
            SPARQLQueryName.SELECT_CSVW_TABLE_SCHEMA_FILE_DEPENDENCIES
        ),
        rdf_graph,
    )

    return map_csvw_table_schemas_file_dependencies_result(results)


def select_units(rdf_graph: rdflib.ConjunctiveGraph) -> List[UnitResult]:
    """
    Queries the units from data set.

    Member of :file:`./sparqlquerymanager.py`

    :return: `List[UnitResult]`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_UNITS),
        rdf_graph,
    )

    return map_units(results)


def select_primary_key_col_names_by_csv_url(
    rdf_graph: rdflib.ConjunctiveGraph, table_url: str
) -> PrimaryKeyColNamesByDatasetUrlResult:
    """
    Queries the primary keys for the given table url.

    Member of :file:`./sparqlquerymanager.py`

    :return: `PrimaryKeyColNamesByDatasetUrlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(
            SPARQLQueryName.SELECT_CODELIST_PRIMARY_KEY_BY_CSV_URL
        ),
        rdf_graph,
        init_bindings={"table_url": Literal(table_url)},
    )

    return map_primary_key_col_names_by_csv_url_result(results)


def select_metadata_dependencies(
    rdf_graph: rdflib.Graph,
) -> List[MetadataDependenciesResult]:
    """
    Queries a CSV-W and extracts metadata dependencies defined by void dataset dataDumps.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_METADATA_DEPENDENCIES),
        rdf_graph,
    )

    return map_metadata_dependency_results(results)


def select_table_schema_properties(
    rdf_graph: rdflib.Graph,
) -> List[TableSchemaPropertiesResult]:
    """
    Queries a CSV-W and extracts about_url, csv_url and a list of the primary key column names for all tables in the CSV-W.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_TABLE_SCHEMA_PROPERTIES),
        rdf_graph,
    )

    return map_table_schema_properties_results(results)


def select_column_definitions(
    rdf_graph: rdflib.Graph,
) -> List[ColumnDefinition]:
    """
    Selects the column names and corresponding column titles.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_COLUMN_DEFINITIONS),
        rdf_graph,
    )

    return map_column_definition_results(results)
