"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union
from urllib.parse import urljoin

import rdflib
from pandas import DataFrame

from csvcubed.cli.inspect.inspectdatasetmanager import (
    get_concepts_hierarchy_info,
    get_dataset_observations_info,
    get_dataset_val_counts_info,
    load_csv_to_dataframe,
)
from csvcubed.models.csvcubedexception import (
    InputNotSupportedException,
    UnsupportedNumOfPrimaryKeyColNamesException,
)
from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.inspectdataframeresults import (
    CodelistHierarchyInfoResult,
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    ColumnDefinition,
    DSDLabelURIResult,
    PrimaryKeyColNamesByDatasetUrlResult,
    QubeComponentsResult,
)
from csvcubed.utils.csvdataset import transform_dataset_to_canonical_shape
from csvcubed.utils.skos.codelist import (
    CodelistPropertyUrl,
    get_codelist_col_title_by_property_url,
    get_codelist_col_title_from_col_name,
)
from csvcubed.utils.sparql_handler.code_list_inspector import CodeListInspector
from csvcubed.utils.sparql_handler.data_cube_state import DataCubeState
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    select_cols_where_suppress_output_is_true,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_dsd_code_list_and_cols,
    select_primary_key_col_names_by_csv_url,
)
from csvcubed.utils.uri import looks_like_uri


@dataclass
class MetadataPrinter:
    """
    This class produces the printables necessary for producing outputs to the CLI.
    """

    state: Union[DataCubeState, CodeListInspector]

    csvw_type_str: str = field(init=False)
    primary_csv_url: str = field(init=False)
    dataset: DataFrame = field(init=False)

    result_catalog_metadata: CatalogMetadataResult = field(init=False)
    result_dataset_label_dsd_uri: DSDLabelURIResult = field(init=False)
    result_qube_components: QubeComponentsResult = field(init=False)
    result_cols_with_suppress_output_true: ColsWithSuppressOutputTrueResult = field(
        init=False
    )
    result_code_lists: CodelistsResult = field(init=False)
    result_dataset_observations_info: DatasetObservationsInfoResult = field(init=False)
    result_dataset_value_counts: DatasetObservationsByMeasureUnitInfoResult = field(
        init=False
    )
    result_code_list_cols: List[ColumnDefinition] = field(init=False)
    result_concepts_hierachy_info: CodelistHierarchyInfoResult = field(init=False)

    @staticmethod
    def get_csvw_type_str(csvw_type: CSVWType) -> str:
        if csvw_type == CSVWType.QbDataSet:
            return "data cube"
        elif csvw_type == CSVWType.CodeList:
            return "code list"
        else:
            raise InputNotSupportedException()

    def get_primary_csv_url(self) -> str:
        """Return the csv_url for the primary table in the graph."""
        primary_metadata = self.state.csvw_inspector.get_primary_catalog_metadata()
        if isinstance(self.state, DataCubeState):
            return self.state.get_cube_identifiers_for_data_set(
                primary_metadata.dataset_uri
            ).csv_url
        elif isinstance(self.state, CodeListInspector):
            return self.state.get_table_identifiers_for_concept_scheme(
                primary_metadata.dataset_uri
            ).csv_url
        else:
            raise InputNotSupportedException()

    @staticmethod
    def get_parent_label_unique_id_col_titles(
        columns: List[ColumnDefinition], primary_key_col: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        parent_notation_col_title = get_codelist_col_title_by_property_url(
            columns, CodelistPropertyUrl.SkosBroader
        )
        label_col_title = get_codelist_col_title_by_property_url(
            columns, CodelistPropertyUrl.RDFLabel
        )
        unique_identifier = get_codelist_col_title_from_col_name(
            columns, primary_key_col
        )

        return (parent_notation_col_title, label_col_title, unique_identifier)

    def generate_general_results(self):
        """
        Generates results related to data cubes and code lists.

        Member of :class:`./MetadataPrinter`.
        """
        csvw_inspector = self.state.csvw_inspector
        csvw_type = csvw_inspector.csvw_type

        self.csvw_type_str = self.get_csvw_type_str(csvw_type)
        self.result_catalog_metadata = csvw_inspector.get_primary_catalog_metadata()
        self.primary_csv_url = self.get_primary_csv_url()
        self.dataset = load_csv_to_dataframe(
            csvw_inspector.csvw_json_path, Path(self.primary_csv_url)
        )
        self.result_dataset_observations_info = get_dataset_observations_info(
            self.dataset,
            csvw_type,
            self.state.get_shape_for_csv(self.primary_csv_url)
            if isinstance(self.state, DataCubeState)
            else None,
        )

    def get_datacube_results(self):
        """
        Generates results specific to data cubes.

        Member of :class:`./MetadataPrinter`.
        """
        assert isinstance(self.state, DataCubeState)  # Make pyright happier

        csvw_inspector = self.state.csvw_inspector

        self.result_qube_components = self.state.get_dsd_qube_components_for_csv(
            self.primary_csv_url
        )

        self.result_dataset_label_dsd_uri = (
            select_csvw_dsd_dataset_label_and_dsd_def_uri(csvw_inspector.rdf_graph)
        )
        self.result_cols_with_suppress_output_true = (
            select_cols_where_suppress_output_is_true(csvw_inspector.rdf_graph)
        )
        self.result_code_lists = select_dsd_code_list_and_cols(
            csvw_inspector.rdf_graph,
            self.result_dataset_label_dsd_uri.dsd_uri,
            csvw_inspector.csvw_json_path,
        )

        (
            canonical_shape_dataset,
            measure_col,
            unit_col,
        ) = transform_dataset_to_canonical_shape(
            self.state,
            self.dataset,
            self.primary_csv_url,
            self.result_qube_components.qube_components,
        )
        self.result_dataset_value_counts = get_dataset_val_counts_info(
            canonical_shape_dataset, measure_col, unit_col
        )

    def generate_codelist_results(self):
        """
        Generates results specific to code lists.

        Member of :class:`./MetadataPrinter`.
        """
        csvw_inspector = self.state.csvw_inspector
        self.result_code_list_cols = csvw_inspector.get_column_definitions_for_csv(
            self.primary_csv_url
        )
        # Retrieving the primary key column names of the code list to identify the unique identifier
        result_table_schema_properties = csvw_inspector.get_table_info_for_csv_url(
            self.primary_csv_url
        )

        primary_key_col_names = result_table_schema_properties.primary_key_col_names

        # Currently, we do not support composite primary keys.
        if len(primary_key_col_names) != 1:
            raise UnsupportedNumOfPrimaryKeyColNamesException(
                num_of_primary_key_col_names=len(primary_key_col_names),
                table_url=self.primary_csv_url,
            )
        (
            parent_col_title,
            label_col_title,
            unique_identifier,
        ) = self.get_parent_label_unique_id_col_titles(
            self.result_code_list_cols, primary_key_col_names[0]
        )
        self.result_concepts_hierachy_info = get_concepts_hierarchy_info(
            self.dataset, parent_col_title, label_col_title, unique_identifier
        )

    def __post_init__(self):
        self.generate_general_results()
        if self.state.csvw_inspector.csvw_type == CSVWType.QbDataSet:
            self.get_datacube_results()
        elif self.state.csvw_inspector.csvw_type == CSVWType.CodeList:
            self.generate_codelist_results()

    @property
    def type_info_printable(self) -> str:
        """
        Returns a printable of file content type.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if self.state.csvw_inspector.csvw_type == CSVWType.QbDataSet:
            return "- This file is a data cube."
        else:
            return "- This file is a code list."

    @property
    def catalog_metadata_printable(self) -> str:
        """
        Returns a printable of catalog metadata (e.g. title, description).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        return f"- The {self.csvw_type_str} has the following catalog metadata:{self.result_catalog_metadata.output_str}"

    @property
    def dsd_info_printable(self) -> str:
        """
        Returns a printable of data structure definition (DSD).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        return f"- The {self.csvw_type_str} has the following data structure definition:{self.result_dataset_label_dsd_uri.output_str}{self.result_qube_components.output_str}{self.result_cols_with_suppress_output_true.output_str}"

    @property
    def codelist_info_printable(self) -> str:
        """
        Returns a printable of data structure definition (DSD) code list information (e.g. column name, type, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        return f"- The {self.csvw_type_str} has the following code list information:{self.result_code_lists.output_str}"

    @property
    def dataset_observations_info_printable(self) -> str:
        """
        Returns a printable of top 10 and last 10 records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        return f"- The {self.csvw_type_str} has the following dataset information:{self.result_dataset_observations_info.output_str}"

    @property
    def dataset_val_counts_by_measure_unit_info_printable(self) -> str:
        """
        Returns a printable of data set value counts broken-down by measure and unit.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        return f"- The {self.csvw_type_str} has the following value counts:{self.result_dataset_value_counts.output_str}"

    @property
    def codelist_hierachy_info_printable(self) -> str:
        """
        Returns a printable of code list concepts hierarchy.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        return f"- The {self.csvw_type_str} has the following concepts information:{self.result_concepts_hierachy_info.output_str}"
