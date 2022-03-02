"""
Inspect SPARQL Query Manager
----------------------------

Collection of SPARQL query handling functions used in the inspect cli.
"""

from enum import Enum
from pathlib import Path
from typing import List

import pandas as pd
from pandas import DataFrame
from rdflib import Graph, URIRef
from rdflib.query import ResultRow

from csvcubed.models.inspectsparqlresults import (
    CatalogMetadataModel,
    CodelistsModel,
    ColsWithSuppressOutputTrueModel,
    DSDLabelURIModel,
    QubeComponentsModel,
    map_catalog_metadata_result,
    map_codelists_sparql_result,
    map_cols_with_supress_output_true_sparql_result,
    map_dataset_label_dsd_uri_sparql_result,
    map_qube_components_sparql_result,
)
from csvcubed.utils.file import get_root_dir_level
from csvcubed.utils.sparql import ask, select


class DatasetUnit(Enum):
    """
    The type of dataset unit.
    """

    SINGLE_UNIT = 0

    MULTI_UNIT = 1


class SPARQLQueryFileName(Enum):
    """
    The file name of sparql query.
    """

    ASK_IS_CODELIST = "ask_is_codelist"

    ASK_IS_QB_DATASET = "ask_is_qb_dataset"

    SELECT_CATALOG_METADATA = "select_catalog_metadata"

    SELECT_DSD_DATASETLABEL_AND_URI = "select_dsd_datasetlabel_and_uri"

    SELECT_DSD_QUBE_COMPONENTS = "select_dsd_qube_components"

    SELECT_COLS_W_SUPPRESS_OUTPUT = "select_cols_w_suppress_output"

    SELECT_CODE_LISTS_AND_COLS = "select_code_lists_and_cols"


def _get_query_string_from_file(queryType: SPARQLQueryFileName) -> str:
    """
    Read the sparql query string from sparql file for the given query type.

    Member of :file:`./inspectsparqlmanager.py`

    :return: `str` - String containing the sparql query.
    """
    file_path = (
        get_root_dir_level("pyproject.toml", Path(__file__))
        / "csvcubed"
        / "cli"
        / "inspect"
        / "inspect_sparql_queries"
        / (queryType.value + ".sparql")
    )

    try:
        with open(
            file_path,
            "r",
        ) as f:
            return f.read()
    except Exception as ex:
        raise Exception(
            f"An error occured while reading sparql query from file '{file_path}'"
        ) from ex


def ask_is_csvw_code_list(rdf_graph: Graph) -> bool:
    """
    Queries whether the given rdf is a code list (i.e. skos:ConceptScheme).

    Member of :file:`./inspectsparqlmanager.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        _get_query_string_from_file(SPARQLQueryFileName.ASK_IS_CODELIST),
        rdf_graph,
    )


def ask_is_csvw_qb_dataset(rdf_graph: Graph) -> bool:
    """
    Queries whether the given rdf is a qb dataset (i.e. qb:Dataset).

    Member of :file:`./inspectsparqlmanager.py`

    :return: `bool` - Boolean specifying whether the rdf is code list (true) or not (false).
    """
    return ask(
        _get_query_string_from_file(SPARQLQueryFileName.ASK_IS_QB_DATASET),
        rdf_graph,
    )


def select_csvw_catalog_metadata(rdf_graph: Graph) -> CatalogMetadataModel:
    """
    Queries catalog metadata such as title, label, issued date/time, modified data/time, etc.

    Member of :file:`./inspectsparqlmanager.py`

    :return: `CatalogMetadataModel`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryFileName.SELECT_CATALOG_METADATA),
        rdf_graph,
    )

    if len(results) != 1:
        raise Exception(f"Expected 1 record, but found {len(results)}")

    return map_catalog_metadata_result(results[0])


def select_csvw_dsd_dataset_label_and_dsd_def_uri(
    rdf_graph: Graph,
) -> DSDLabelURIModel:
    """
    Queries data structure definition dataset label and uri.

    Member of :file:`./inspectsparqlmanager.py`

    :return: `DSDLabelURIModel`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(
            SPARQLQueryFileName.SELECT_DSD_DATASETLABEL_AND_URI
        ),
        rdf_graph,
    )

    if len(results) != 1:
        raise Exception(f"Expected 1 record, but found {len(results)}")

    return map_dataset_label_dsd_uri_sparql_result(results[0])


def select_csvw_dsd_qube_components(
    rdf_graph: Graph, dsd_uri: str, json_path: Path
) -> QubeComponentsModel:
    """
    Queries the list of qube components.

    Member of :file:`./inspectsparqlmanager.py`

    :return: `QubeComponentsModel`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryFileName.SELECT_DSD_QUBE_COMPONENTS),
        rdf_graph,
        init_bindings={"dsd_uri": URIRef(dsd_uri)},
    )
    return map_qube_components_sparql_result(results, json_path)


def select_cols_where_supress_output_is_true(
    rdf_graph: Graph,
) -> ColsWithSuppressOutputTrueModel:
    """
    Queries the columns where suppress output is true.

    Member of :file:`./inspectsparqlmanager.py`

    :return: `ColsWithSupressOutputTrueSparlqlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryFileName.SELECT_COLS_W_SUPPRESS_OUTPUT),
        rdf_graph,
    )
    return map_cols_with_supress_output_true_sparql_result(results)


def select_dsd_code_list_and_cols(
    rdf_graph: Graph, dsd_uri: str, json_path: Path
) -> CodelistsModel:
    """
    Queries code lists and columns in the data cube.

    Member of :file:`./inspectsparqlmanager.py`

    :return: `CodelistInfoSparqlResult`
    """
    results: List[ResultRow] = select(
        _get_query_string_from_file(SPARQLQueryFileName.SELECT_CODE_LISTS_AND_COLS),
        rdf_graph,
        init_bindings={"dsd_uri": URIRef(dsd_uri)},
    )
    return map_codelists_sparql_result(results, json_path)


def select_datacube_csv_url(dataset_uri: str) -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return "TODO"


def select_codelist_csv_url() -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return "TODO"


def select_datacube_url() -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return "TODO"


def get_dataset_unit_type() -> DatasetUnit:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return DatasetUnit.SINGLE_UNIT


def get_dsd_single_measure() -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return ""


def get_measure_column() -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return "ColMeasure"


def get_dsd_single_unit() -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return ""


def get_units_column() -> str:
    """
    TODO: Description

    Member of :file:`./inspectsparqlmanager.py`

    :return: `TODO`
    """
    return "ColUnits"
