"""
SPARQL query results
----------------------------
"""

import logging
from dataclasses import dataclass
from os import linesep
from pathlib import Path
from typing import Any, Dict, List, Optional

from csvcubedmodels.dataclassbase import DataClassBase
from rdflib.query import ResultRow

from csvcubed.utils.iterables import group_by
from csvcubed.utils.printable import (
    get_printable_list_str,
    get_printable_tabular_list_str,
    get_printable_tabular_str_from_list,
)
from csvcubed.utils.qb.components import (
    ComponentPropertyType,
    get_component_property_as_relative_path,
    get_component_property_type,
)
from csvcubed.utils.sparql_handler.sparql import none_or_map

_logger = logging.getLogger(__name__)


@dataclass
class CatalogMetadataResult:
    """
    Model to represent select catalog metadata sparql query result.
    """

    dataset_uri: str
    """Data set here doesn't necessarily mean the qb:DataSet. It means eiither the qb:DataSet or the skos:ConceptScheme."""
    graph_uri: str
    """URI representing the grapgh in which the Catalog Metadata was found."""
    title: str
    label: str
    issued: str
    modified: str
    license: str
    creator: str
    publisher: str
    landing_pages: list[str]
    themes: list[str]
    keywords: list[str]
    contact_point: str
    identifier: str
    comment: str
    description: str

    @property
    def output_str(self) -> str:
        formatted_landing_pages: str = get_printable_list_str(self.landing_pages)
        formatted_themes: str = get_printable_list_str(self.themes)
        formatted_keywords: str = get_printable_list_str(self.keywords)
        formatted_description: str = self.description.replace(linesep, f"{linesep}\t\t")
        return f"""
        - Title: {self.title}
        - Label: {self.label}
        - Issued: {self.issued}
        - Modified: {self.modified}
        - License: {self.license}
        - Creator: {self.creator}
        - Publisher: {self.publisher}
        - Landing Pages: {formatted_landing_pages}
        - Themes: {formatted_themes}
        - Keywords: {formatted_keywords}
        - Contact Point: {self.contact_point}
        - Identifier: {self.identifier}
        - Comment: {self.comment}
        - Description: {formatted_description}
        """


@dataclass
class DSDLabelURIResult:
    """
    Model to represent select dsd dataset label and uri sparql query result.
    """

    dataset_label: str
    dsd_uri: str

    @property
    def output_str(self) -> str:
        return f"""
        - Dataset Label: {self.dataset_label}"""


@dataclass
class CubeTableIdentifiers(DataClassBase):
    """
    Links the CSV, DataSet and DataStructureDefinition URIs for a given cube.
    """

    csv_url: str
    data_set_url: str
    dsd_uri: str


@dataclass
class ColsWithSuppressOutputTrueResult:
    """
    Model to represent select cols where the suppress output is true sparql query result.
    """

    columns: list[str]

    @property
    def output_str(self) -> str:
        return f"""
        - Columns where suppress output is true: {get_printable_list_str(self.columns)}"""


@dataclass
class CodelistResult(DataClassBase):
    """
    Model to represent a codelist.
    """

    code_list: str
    code_list_label: str
    cols_used_in: str


@dataclass
class CSVWTableSchemaFileDependenciesResult:
    """
    Model to represent select csvw table schema file dependencies result.
    """

    table_schema_file_dependencies: List[str]


@dataclass
class CodelistsResult:
    """
    Model to represent select codelists sparql query result.
    """

    codelists: list[CodelistResult]
    num_codelists: int

    @property
    def output_str(self) -> str:
        formatted_codelists = get_printable_tabular_str_from_list(
            [
                codelist.as_dict()
                for codelist in sorted(self.codelists, key=lambda c: c.code_list)
            ],
            column_names=["Code List", "Code List Label", "Columns Used In"],
        )
        return f"""
        - Number of Code Lists: {self.num_codelists}
        - Code Lists:{linesep}{formatted_codelists}"""


@dataclass
class CsvUrlResult:
    """
    Model to represent select csv url result.
    """

    csv_url: str


@dataclass
class UnitResult:
    """
    Model to represent select single unit from dsd.
    """

    unit_uri: str
    unit_label: str


@dataclass
class CodelistColumnResult(DataClassBase):
    """
    Model to represent a codelist column.
    """

    column_property_url: Optional[str]
    column_value_url: Optional[str]
    column_title: Optional[str]
    column_name: Optional[str]


@dataclass
class CodeListColsByDatasetUrlResult:
    """
    Model to represent select codelist columns by table url.
    """

    columns: List[CodelistColumnResult]


@dataclass
class PrimaryKeyColNameByDatasetUrlResult:
    """
    Model to represent select primary key column name by table url.
    """

    value: str


@dataclass
class PrimaryKeyColNamesByDatasetUrlResult:
    """
    Model to represent select primary keys by table url.
    """

    primary_key_col_names: List[PrimaryKeyColNameByDatasetUrlResult]


@dataclass
class MetadataDependenciesResult:
    """
    Model representing a metadata dependency which should be loaded to make sense of the current graph.
    """

    data_set: str
    data_dump: str
    uri_space: str


@dataclass
class TableSchemaPropertiesResult:
    """
    Model representing the table schema value url and about url.
    """

    about_url: str
    value_url: str
    table_url: str


@dataclass
class IsPivotedShapeMeasureResult:
    """
    A dataclass that is used to return the measure of from a cube's metadata and whether that measure is part of a
    pivoted or standard shape cube.
    """

    csv_url: str
    measure: str
    is_pivoted_shape: bool


@dataclass(unsafe_hash=True)
class ColumnDefinition:
    """
    Model representing the Column Titles and Column Names of a data set.

    See https://www.w3.org/TR/2015/REC-tabular-data-model-20151217/#dfn-column for the full list of properties a CSV-W
    column can have.

    N.B. This does not contain all possible CSV-W column properties, just the ones currently used by csvcubed.
    """

    csv_url: str
    """CSV that this column is defined against."""
    about_url: Optional[str]
    data_type: Optional[str]
    name: str
    property_url: Optional[str]
    required: bool
    suppress_output: bool
    title: Optional[str]
    """This should technically be a list according to the W3C spec."""
    value_url: Optional[str]
    virtual: bool


@dataclass
class QubeComponentResult(DataClassBase):
    """
    Model to represent a qube component.
    """

    component: str
    dsd_uri: str
    property: str
    property_label: Optional[str]
    property_type: str
    real_columns_used_in: List[ColumnDefinition]
    """The CSV columns this component is used in."""
    used_by_observed_value_columns: List[ColumnDefinition]
    """The Observed Value CSV Columns this component describes."""
    required: bool


@dataclass
class QubeComponentsResult:
    """
    Model to represent select qube components sparql query result.
    """

    qube_components: list[QubeComponentResult]
    num_components: int

    @property
    def output_str(self) -> str:
        component_dicts: List[Dict] = []
        for component in self.qube_components:
            component_dicts.append(
                {
                    "Property": component.property,
                    "Property Label": component.property_label,
                    "Property Type": component.property_type,
                    "Column Title": ", ".join(
                        [
                            c.title
                            for c in component.real_columns_used_in
                            if c.title is not None
                        ]
                    ),
                    "Observation Value Column Titles": ", ".join(
                        [
                            c.title
                            for c in component.used_by_observed_value_columns
                            if c.title is not None
                        ]
                    ),
                    "Required": component.required,
                }
            )

        formatted_components = get_printable_tabular_str_from_list(
            component_dicts,
            column_names=[
                "Property",
                "Property Label",
                "Property Type",
                "Column Title",
                "Observation Value Column Titles",
                "Required",
            ],
        )
        return f"""
        - Number of Components: {self.num_components}
        - Components:{linesep}{formatted_components}"""


def map_catalog_metadata_results(
    sparql_results: List[ResultRow],
) -> List[CatalogMetadataResult]:
    """
    Maps the sparql query results to a list of `CatalogMetadataResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `List[CatalogMetadataResult]`
    """
    results: List[CatalogMetadataResult] = []
    for row in sparql_results:
        result_dict = row.asdict()

        result = CatalogMetadataResult(
            graph_uri=str(result_dict["graph"]),
            dataset_uri=str(result_dict["dataset"]),
            title=str(result_dict["title"]),
            label=str(result_dict["label"]),
            issued=str(result_dict["issued"]),
            modified=str(result_dict["modified"]),
            comment=none_or_map(result_dict.get("comment"), str) or "None",
            description=none_or_map(result_dict.get("description"), str) or "None",
            license=none_or_map(result_dict.get("license"), str) or "None",
            creator=none_or_map(result_dict.get("creator"), str) or "None",
            publisher=none_or_map(result_dict.get("publisher"), str) or "None",
            landing_pages=str(result_dict["landingPages"]).split("|"),
            themes=str(result_dict["themes"]).split("|"),
            keywords=str(result_dict["keywords"]).split("|"),
            contact_point=none_or_map(result_dict.get("contactPoint"), str) or "None",
            identifier=none_or_map(result_dict.get("identifier"), str) or "None",
        )
        results.append(result)

    return results


def map_dataset_label_dsd_uri_sparql_result(
    sparql_result: ResultRow,
) -> DSDLabelURIResult:
    """
    Maps sparql query result to `DSDLabelURIResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `DSDLabelURIResult`
    """
    result_dict = sparql_result.asdict()

    result = DSDLabelURIResult(
        dataset_label=str(result_dict["dataSetLabel"]),
        dsd_uri=str(result_dict["dataStructureDefinition"]),
    )
    return result


def map_data_set_dsd_csv_url_result(
    sparql_results: List[ResultRow],
) -> List[CubeTableIdentifiers]:
    """
    TODO: Add description
    """

    def map_row(row_result: Dict[str, Any]) -> CubeTableIdentifiers:
        return CubeTableIdentifiers(
            csv_url=str(row_result["csvUrl"]),
            data_set_url=str(row_result["dataSet"]),
            dsd_uri=str(row_result["dsd"]),
        )

    return [map_row(row.asdict()) for row in sparql_results]


def _map_qube_component_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> QubeComponentResult:
    """
    Maps sparql query result to `QubeComponentResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `QubeComponentResult`
    """
    result_dict = sparql_result.asdict()
    _logger.debug("result_dict: %s", result_dict)

    result = QubeComponentResult(
        component=str(result_dict["component"]),
        dsd_uri=str(result_dict["dsdUri"]),
        property=get_component_property_as_relative_path(
            json_path, str(result_dict["componentProperty"])
        ),
        property_label=(
            none_or_map(result_dict.get("componentPropertyLabel"), str) or ""
        ),
        property_type=get_component_property_type(
            str(result_dict["componentPropertyType"])
        ),
        required=none_or_map(result_dict.get("required"), bool) or False,
        # The following two properties are populated later using the results from the CSV-W columns query.
        real_columns_used_in=[],
        used_by_observed_value_columns=[],
    )
    return result


def map_qube_components_sparql_result(
    sparql_results_dsd_components: List[ResultRow],
    json_path: Path,
    map_dsd_uri_to_csv_url: Dict[str, str],
    map_csv_url_to_column_definitions: Dict[str, List[ColumnDefinition]],
) -> Dict[str, QubeComponentsResult]:
    """
    Returns a map of csv_url to `QubeComponentsResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `Dict[str, QubeComponentsResult]`
    """
    components: List[QubeComponentResult] = [
        _map_qube_component_sparql_result(r, json_path)
        for r in sparql_results_dsd_components
    ]

    map_dsd_uri_to_components = group_by(components, lambda c: c.dsd_uri)

    for (dsd_uri, components) in map_dsd_uri_to_components.items():
        csv_url = map_dsd_uri_to_csv_url[dsd_uri]
        csv_column_definitions = map_csv_url_to_column_definitions[csv_url]

        measure_uris = {
            c.property
            for c in components
            if c.property_type == str(ComponentPropertyType.Measure.value)
        }

        observed_value_columns = [
            c
            for c in csv_column_definitions
            if (not c.virtual) and c.property_url in measure_uris
        ]

        for component in components:
            all_columns_used_in = [
                c
                for c in csv_column_definitions
                if c.property_url == component.property
            ]

            component.real_columns_used_in = [
                c for c in all_columns_used_in if (not c.virtual)
            ]

            component.required = component.required or any(
                c.required for c in component.real_columns_used_in
            )

            columns_using_this_component_about_urls = {
                c.about_url for c in all_columns_used_in
            }

            component.used_by_observed_value_columns = [
                c
                for c in observed_value_columns
                if c.about_url in columns_using_this_component_about_urls
            ]

    return {
        map_dsd_uri_to_csv_url[dsd_uri]: QubeComponentsResult(
            qube_components=components, num_components=len(components)
        )
        for (dsd_uri, components) in map_dsd_uri_to_components.items()
    }


def map_cols_with_supress_output_true_sparql_result(
    sparql_results: List[ResultRow],
) -> ColsWithSuppressOutputTrueResult:
    """
    Maps sparql query result to `ColsWithSuppressOutputTrueResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `ColsWithSuppressOutputTrueResult`
    """
    columns = list(
        map(
            lambda result: str(result["csvColumnTitle"]),
            sparql_results,
        )
    )
    result = ColsWithSuppressOutputTrueResult(columns=columns)
    return result


def _map_codelist_sparql_result(
    sparql_result: ResultRow, json_path: Path
) -> CodelistResult:
    """
    Maps sparql query result to `CodelistResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodelistResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistResult(
        code_list=get_component_property_as_relative_path(
            json_path, str(result_dict["codeList"])
        ),
        code_list_label=none_or_map(result_dict.get("codeListLabel"), str) or "",
        cols_used_in=get_printable_tabular_list_str(
            str(result_dict["csvColumnsUsedIn"]).split("|")
        ),
    )
    return result


def map_codelists_sparql_result(
    sparql_results: List[ResultRow], json_path: Path
) -> CodelistsResult:
    """
    Maps sparql query result to `CodelistsModel`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodelistsModel`
    """
    codelists = list(
        map(
            lambda result: _map_codelist_sparql_result(result, json_path),
            sparql_results,
        )
    )
    result = CodelistsResult(codelists=codelists, num_codelists=len(codelists))
    return result


def map_csvw_table_schemas_file_dependencies_result(
    sparql_results: List[ResultRow],
) -> CSVWTableSchemaFileDependenciesResult:
    """
    Maps sparql query result to `CSVWTableSchemaFileDependenciesResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CSVWTableSchemaFileDependenciesResult`
    """

    result = CSVWTableSchemaFileDependenciesResult(
        table_schema_file_dependencies=[
            str(sparql_result["tableSchema"]) for sparql_result in sparql_results
        ]
    )
    return result


def map_csv_url_result(
    sparql_result: ResultRow,
) -> CsvUrlResult:
    """
    Maps sparql query result to `CsvUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CsvUrlResult`
    """
    result_dict = sparql_result.asdict()

    result = CsvUrlResult(csv_url=str(result_dict["tableUrl"]))
    return result


def map_units(sparql_results: List[ResultRow]) -> List[UnitResult]:
    """
    Maps sparql query result to `UnitResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `UnitResult`
    """

    def map_row(row_result: Dict[str, Any]) -> UnitResult:
        return UnitResult(
            unit_uri=str(row_result["unit"]), unit_label=str(row_result["unitLabel"])
        )

    return [map_row(row.asdict()) for row in sparql_results]


def _map_codelist_column_sparql_result(
    sparql_result: ResultRow,
) -> CodelistColumnResult:
    """
    Maps sparql query result to `CodelistColumnResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodelistColumnResult`
    """
    result_dict = sparql_result.asdict()

    result = CodelistColumnResult(
        column_property_url=none_or_map(result_dict.get("columnPropertyUrl"), str),
        column_value_url=none_or_map(result_dict.get("columnValueUrl"), str),
        column_title=none_or_map(result_dict.get("columnTitle"), str),
        column_name=none_or_map(result_dict.get("columnName"), str),
    )
    return result


def map_codelist_cols_by_csv_url_result(
    sparql_results: List[ResultRow],
) -> CodeListColsByDatasetUrlResult:
    """
    Maps sparql query result to `CodeListColsByDatasetUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `CodeListColsByDatasetUrlResult`
    """

    columns = list(
        map(
            lambda result: _map_codelist_column_sparql_result(result),
            sparql_results,
        )
    )
    result = CodeListColsByDatasetUrlResult(columns=columns)
    return result


def _map_primary_key_col_name_by_csv_url_result(
    sparql_result: ResultRow,
) -> PrimaryKeyColNameByDatasetUrlResult:
    """
    Maps sparql query result to `PrimaryKeyColNameByDatasetUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `PrimaryKeyColNameByDatasetUrlResult`
    """
    result_dict = sparql_result.asdict()

    result = PrimaryKeyColNameByDatasetUrlResult(
        value=str(result_dict["tablePrimaryKey"]),
    )
    return result


def map_primary_key_col_names_by_csv_url_result(
    sparql_results: List[ResultRow],
) -> PrimaryKeyColNamesByDatasetUrlResult:
    """
    Maps sparql query result to `PrimaryKeyColNamesByDatasetUrlResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `PrimaryKeyColNamesByDatasetUrlResult`
    """
    primary_key_col_names = list(
        map(
            lambda result: _map_primary_key_col_name_by_csv_url_result(result),
            sparql_results,
        )
    )
    result = PrimaryKeyColNamesByDatasetUrlResult(
        primary_key_col_names=primary_key_col_names
    )
    return result


def map_metadata_dependency_results(
    sparql_results: List[ResultRow],
) -> List[MetadataDependenciesResult]:
    def map_row(row_result: Dict[str, Any]) -> MetadataDependenciesResult:
        return MetadataDependenciesResult(
            data_set=str(row_result["dataset"]),
            data_dump=str(row_result["dataDump"]),
            uri_space=str(row_result["uriSpace"]),
        )

    return [map_row(row.asdict()) for row in sparql_results]


def map_table_schema_properties_result(
    sparql_result: ResultRow,
) -> TableSchemaPropertiesResult:
    """
    Maps sparql query result to `TableSchemaPropertiesResult`

    Member of :file:`./models/sparqlresults.py`

    :return: `TableSchemaPropertiesResult`
    """
    result_dict = sparql_result.asdict()

    result = TableSchemaPropertiesResult(
        about_url=str(result_dict["tableAboutUrl"]),
        value_url=str(result_dict["columnValueUrl"]),
        table_url=str(result_dict["csvUrl"]),
    )
    return result


def map_is_pivoted_shape_for_measures_in_data_set(
    sparql_results: List[ResultRow],
) -> List[IsPivotedShapeMeasureResult]:
    """
    Maps the sparql query result to objects of type IsPivotedMeasureResult that are then returned.
    """

    def map_row(row_result: Dict[str, Any]) -> IsPivotedShapeMeasureResult:
        return IsPivotedShapeMeasureResult(
            csv_url=str(row_result["csvUrl"]),
            measure=str(row_result["measure"]),
            is_pivoted_shape=bool(row_result["isPivotedShape"]),
        )

    return [map_row(row.asdict()) for row in sparql_results]


def map_column_definition_results(
    sparql_results: List[ResultRow],
) -> List[ColumnDefinition]:
    """
    Maps SPARQL query results to 'ColumnDefinition's.
    """

    def map_row(row_result: Dict[str, Any]) -> ColumnDefinition:
        return ColumnDefinition(
            csv_url=str(row_result["csvUrl"]),
            about_url=none_or_map(row_result.get("aboutUrl"), str),
            data_type=none_or_map(row_result.get("dataType"), str),
            name=str(row_result["name"]),
            property_url=none_or_map(row_result.get("propertyUrl"), str),
            required=bool(row_result["required"]),
            suppress_output=bool(row_result["suppressOutput"]),
            title=none_or_map(row_result.get("title"), str),
            value_url=none_or_map(row_result.get("valueUrl"), str),
            virtual=bool(row_result.get("virtual")),
        )

    return [map_row(row.asdict()) for row in sparql_results]
