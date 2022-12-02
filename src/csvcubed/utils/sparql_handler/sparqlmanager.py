"""
SPARQL Queries
----------------------

Collection of SPARQL queries.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional

import rdflib
from rdflib import Literal, URIRef
from rdflib.query import ResultRow

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.models.csvcubedexception import (
    FailedToReadSparqlQueryException,
    FeatureNotSupportedException,
    InvalidNumberOfRecordsException,
)
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.sparqlresults import (
    CSVWTableSchemaFileDependenciesResult,
    CatalogMetadataResult,
    CodeListColsByDatasetUrlResult,
    ColTitlesAndNamesResult,
    IsPivotedShapeMeasureResult,
    ObservationValueColumnTitleAboutUrlResult,
    PrimaryKeyColNamesByDatasetUrlResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    DSDLabelURIResult,
    DSDSingleUnitResult,
    CsvUrlResult,
    QubeComponentsResult,
    MetadataDependenciesResult,
    TableSchemaPropertiesResult,
    UnitColumnAboutValueUrlResult,
    map_catalog_metadata_result,
    map_codelist_cols_by_csv_url_result,
    map_col_tiles_and_names_result,
    map_is_pivoted_shape_for_measures_in_data_set,
    map_observation_value_col_title_and_about_url_result,
    map_primary_key_col_names_by_csv_url_result,
    map_codelists_sparql_result,
    map_cols_with_supress_output_true_sparql_result,
    map_csvw_table_schemas_file_dependencies_result,
    map_dataset_label_dsd_uri_sparql_result,
    map_csv_url_result,
    map_qube_components_sparql_result,
    map_single_unit_from_dsd_result,
    map_metadata_dependency_results,
    map_table_schema_properties_result,
    map_unit_col_about_value_urls_result,
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

    SELECT_DSD_QUBE_COMPONENTS = "select_dsd_qube_components"

    SELECT_OBS_VAL_FOR_DSD_COMPONENT_PROPERTIES = (
        "select_obs_val_for_dsd_component_properties"
    )

    SELECT_COLS_W_SUPPRESS_OUTPUT = "select_cols_w_suppress_output"

    SELECT_CODELISTS_AND_COLS = "select_codelists_and_cols"

    SELECT_QB_CSV_URL = "select_qb_csv_url"

    SELECT_CODELIST_CSV_URL = "select_codelist_csv_url"

    SELECT_SINGLE_UNIT_FROM_DSD = "select_single_unit_from_dsd"

    SELECT_CSVW_TABLE_SCHEMA_FILE_DEPENDENCIES = (
        "select_csvw_table_schema_file_dependencies"
    )

    SELECT_CODELIST_COLS_BY_CSV_URL = "select_codelist_cols_by_csv_url"

    SELECT_CODELIST_PRIMARY_KEY_BY_CSV_URL = (
        "select_codelist_primary_key_by_csv_url"
    )

    SELECT_METADATA_DEPENDENCIES = "select_metadata_dependencies"

    SELECT_TABLE_SCHEMA_PROPERTIES = "select_table_schema_properties"

    SELECT_IS_PIVOTED_SHAPE_FOR_MEASURES_IN_DATA_SET = (
        "select_is_pivoted_shape_for_measures_in_data_set"
    )

    SELECT_UNIT_COL_ABOUT_AND_VALUE_URLS = "select_unit_col_about_and_value_urls"
    
    SELECT_UNIT_COL_OBSERVED_COL_TITLE_AND_ABOUT_URL = "select_unit_col_observed_col_title_and_about_url"
    
    SELECT_COL_TITLES_AND_NAMES = "select_col_titles_and_names"

def _get_query_string_from_file(queryType: SPARQLQueryName) -> str:
    """
    Read the sparql query string from sparql file for the given query type.

    Member of :file:`./sparqlmanager.py`

    :return: `str` - String containing the sparql query.
    """
    _logger.debug(f"Root path: {APP_ROOT_DIR_PATH.absolute()}")

    file_path: Path = (
        APP_ROOT_DIR_PATH
        / "utils"
        / "sparql_handler"
        / "sparql_queries"
        / (queryType.value + ".sparql")
    )
    _logger.debug(f"{queryType.value} query file path: {file_path.absolute()}")

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

    Member of :file:`./sparqlmanager.py`

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

    Member of :file:`./sparqlmanager.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        SPARQLQueryName.ASK_IS_QB_DATASET.ASK_IS_QB_DATASET.value,
        _get_query_string_from_file(SPARQLQueryName.ASK_IS_QB_DATASET),
        rdf_graph,
    )


def select_csvw_catalog_metadata(rdf_graph: rdflib.Graph) -> CatalogMetadataResult:
    """
    Queries catalog metadata such as title, label, issued date/time, modified data/time, etc.

    Member of :file:`./sparqlmanager.py`

    :return: `CatalogMetadataResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_CATALOG_METADATA),
        rdf_graph,
    )

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_CATALOG_METADATA.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )

    return map_catalog_metadata_result(results[0])


def select_csvw_dsd_dataset_label_and_dsd_def_uri(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> DSDLabelURIResult:
    """
    Queries data structure definition dataset label and uri.

    Member of :file:`./sparqlmanager.py`

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


def select_csvw_dsd_qube_components(
    cube_shape: Optional[CubeShape],
    rdf_graph: rdflib.ConjunctiveGraph,
    dsd_uri: str,
    json_path: Path,
) -> QubeComponentsResult:
    """
    Queries the list of qube components.

    Member of :file:`./sparqlmanager.py`

    :return: `QubeComponentsResult`
    """
    result_dsd_components: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_DSD_QUBE_COMPONENTS),
        rdf_graph,
        init_bindings={"dsd_uri": URIRef(dsd_uri)},
    )

    result_observation_val_col_titles: Optional[List[ResultRow]] = None
    if cube_shape == CubeShape.Pivoted:
        result_observation_val_col_titles = select(
            _get_query_string_from_file(
                SPARQLQueryName.SELECT_OBS_VAL_FOR_DSD_COMPONENT_PROPERTIES
            ),
            rdf_graph,
            init_bindings={"dsd_uri": URIRef(dsd_uri)},
        )

    return map_qube_components_sparql_result(
        result_dsd_components, result_observation_val_col_titles, json_path
    )


def select_is_pivoted_shape_for_measures_in_data_set(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> List[IsPivotedShapeMeasureResult]:
    """
    Queries the measure and whether it is a part of a pivoted or standard shape cube.
    """
    result_is_pivoted_shape: List[ResultRow] = select(
        _get_query_string_from_file(
            SPARQLQueryName.SELECT_IS_PIVOTED_SHAPE_FOR_MEASURES_IN_DATA_SET
        ),
        rdf_graph,
    )

    return map_is_pivoted_shape_for_measures_in_data_set(result_is_pivoted_shape)


def select_cols_where_suppress_output_is_true(
    rdf_graph: rdflib.ConjunctiveGraph,
) -> ColsWithSuppressOutputTrueResult:
    """
    Queries the columns where suppress output is true.

    Member of :file:`./sparqlmanager.py`

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

    Member of :file:`./sparqlmanager.py`

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

    Member of :file:`./sparqlmanager.py`

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

    Member of :file:`./sparqlmanager.py`

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

    Member of :file:`./sparqlmanager.py`

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


def select_single_unit_from_dsd(
    rdf_graph: rdflib.ConjunctiveGraph, dataset_uri: str, json_path: Path
) -> DSDSingleUnitResult:
    """
    Queries the single unit uri and label from the data structure definition.

    Member of :file:`./sparqlmanager.py`

    :return: `DSDSingleUnitResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_SINGLE_UNIT_FROM_DSD),
        rdf_graph,
        init_bindings={"dataset_uri": Literal(dataset_uri)},
    )

    if len(results) != 1:
        raise InvalidNumberOfRecordsException(
            record_description=f"result for the {SPARQLQueryName.SELECT_SINGLE_UNIT_FROM_DSD.value} sparql query",
            excepted_num_of_records=1,
            num_of_records=len(results),
        )
    return map_single_unit_from_dsd_result(results[0], json_path)


def select_codelist_cols_by_csv_url(
    rdf_graph: rdflib.ConjunctiveGraph, table_url: str
) -> CodeListColsByDatasetUrlResult:
    """
    Queries the code list column property and value urls for the given table url.

    Member of :file:`./sparqlmanager.py`

    :return: `CodeListColsByDatasetUrlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(
            SPARQLQueryName.SELECT_CODELIST_COLS_BY_CSV_URL
        ),
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

    Member of :file:`./sparqlmanager.py`

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


def select_unit_col_about_value_urls(
    rdf_graph: rdflib.Graph,
) -> List[UnitColumnAboutValueUrlResult]:
    """
    Queries a CSV-W and extracts the unit column's about and value urls.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_UNIT_COL_ABOUT_AND_VALUE_URLS),
        rdf_graph,
    )

    return map_unit_col_about_value_urls_result(results)

def select_observation_value_column_title_and_about_url(
    rdf_graph: rdflib.Graph,
) -> List[ObservationValueColumnTitleAboutUrlResult]:
    """
    Queries a CSV-W and extracts the observation value column title and about url.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_UNIT_COL_OBSERVED_COL_TITLE_AND_ABOUT_URL),
        rdf_graph,
    )

    return map_observation_value_col_title_and_about_url_result(results)

def select_col_titles_and_names(
    rdf_graph: rdflib.Graph,
) -> List[ColTitlesAndNamesResult]:
    """
    Selects the column names and corresponding column titles.
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryName.SELECT_COL_TITLES_AND_NAMES),
        rdf_graph,
    )

    return map_col_tiles_and_names_result(results)