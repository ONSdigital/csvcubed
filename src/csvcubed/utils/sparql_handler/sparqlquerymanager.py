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
    FeatureNotSupportedException,
    InvalidNumberOfRecordsException,
)
from csvcubed.models.sparql.valuesbinding import ValuesBinding
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodeListColsByDatasetUrlResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    ColumnDefinition,
    CsvUrlResult,
    CSVWTableSchemaFileDependenciesResult,
    CubeTableIdentifiers,
    DSDLabelURIResult,
    IsPivotedShapeMeasureResult,
    MetadataDependenciesResult,
    PrimaryKeyColNamesByDatasetUrlResult,
    QubeComponentsResult,
    TableSchemaPropertiesResult,
    UnitResult,
    map_catalog_metadata_results,
    map_codelist_cols_by_csv_url_result,
    map_codelists_sparql_result,
    map_cols_with_supress_output_true_sparql_result,
    map_column_definition_results,
    map_csv_url_result,
    map_csvw_table_schemas_file_dependencies_result,
    map_data_set_dsd_csv_url_result,
    map_dataset_label_dsd_uri_sparql_result,
    map_is_pivoted_shape_for_measures_in_data_set,
    map_metadata_dependency_results,
    map_primary_key_col_names_by_csv_url_result,
    map_qube_components_sparql_result,
    map_table_schema_properties_result,
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

    SELECT_DSD_DATASETLABEL_AND_URI = "select_dsd_datasetlabel_and_uri"

    SELECT_DATA_SET_DSD_CSV_URL = "select_data_set_dsd_csv_url"

    SELECT_DSD_QUBE_COMPONENTS = "select_dsd_qube_components"

    SELECT_COLS_W_SUPPRESS_OUTPUT = "select_cols_w_suppress_output"

    SELECT_CODELISTS_AND_COLS = "select_codelists_and_cols"

    SELECT_QB_CSV_URL = "select_qb_csv_url"

    SELECT_CODELIST_CSV_URL = "select_codelist_csv_url"

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


def select_csvw_dsd_dataset_label_and_dsd_def_uri(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> DSDLabelURIResult:
    """
    Queries data structure definition dataset label and uri.

    Member of :file:`./sparqlquerymanager.py`

    :return: `DSDLabelURIResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_DSD_DATASETLABEL_AND_URI),
        rdf_graph,
    )

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_DSD_DATASETLABEL_AND_URI.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )
    return map_dataset_label_dsd_uri_sparql_result(results[0])


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


def select_cols_where_suppress_output_is_true(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> ColsWithSuppressOutputTrueResult:
    """
    Queries the columns where suppress output is true.

    Member of :file:`./sparqlquerymanager.py`

    :return: `ColsWithSupressOutputTrueSparlqlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_COLS_W_SUPPRESS_OUTPUT),
        rdf_graph,
    )
    return map_cols_with_supress_output_true_sparql_result(results)


def select_dsd_code_list_and_cols(
    rdf_graph: rdflib.ConjunctiveGraph, dsd_uri: str, json_path: Path
) -> CodelistsResult:
    """
    Queries code lists and columns in the data cube.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CodelistInfoSparqlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_CODELISTS_AND_COLS),
        rdf_graph,
        init_bindings={"dsd_uri": URIRef(dsd_uri)},
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


def select_qb_csv_url(
    rdf_graph: rdflib.ConjunctiveGraph, dataset_uri: str
) -> CsvUrlResult:
    """
    Queries the url of the given qb:dataset.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CsvUrlResult`
    """
    if not dataset_uri.startswith("file://"):
        raise FeatureNotSupportedException(
            explanation="This query is used by the inspect command. Currently, the inspect command only supports reading the csv when the url is a file path. In the future, it will support reading the csv when the url is a web address"
        )

    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_QB_CSV_URL),
        rdf_graph,
        init_bindings={"dataset_uri": Literal(dataset_uri)},
    )
    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_QB_CSV_URL.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )
    return map_csv_url_result(results[0])


def select_codelist_csv_url(rdf_graph: rdflib.ConjunctiveGraph) -> CsvUrlResult:
    """
    Queries the url of the given skos:conceptScheme.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CsvUrlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_CODELIST_CSV_URL),
        rdf_graph,
    )
    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_CODELIST_CSV_URL.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )
    return map_csv_url_result(results[0])


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


def select_codelist_cols_by_csv_url(
    rdf_graph: rdflib.ConjunctiveGraph, table_url: str
) -> CodeListColsByDatasetUrlResult:
    """
    Queries the code list column property and value urls for the given table url.

    Member of :file:`./sparqlquerymanager.py`

    :return: `CodeListColsByDatasetUrlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_CODELIST_COLS_BY_CSV_URL),
        rdf_graph,
        init_bindings={"table_url": Literal(table_url)},
    )

    if len(results) < 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_CODELIST_COLS_BY_CSV_URL.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )
    return map_codelist_cols_by_csv_url_result(results)


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
) -> TableSchemaPropertiesResult:
    """
    Queries a CSV-W and extracts table url, about url and value url from the table with skos:inScheme property url.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_TABLE_SCHEMA_PROPERTIES),
        rdf_graph,
    )

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_TABLE_SCHEMA_PROPERTIES.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )

    return map_table_schema_properties_result(results[0])


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
