"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import pandas as pd

from rdflib import Graph

from csvcubed.models.inspectsparqlresults import (
    CatalogMetadataResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    DSDLabelURIResult,
    DatasetURLResult,
    QubeComponentResult,
    QubeComponentsResult,
)
from csvcubed.cli.inspect.metadatainputvalidator import CSVWType
from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_codelist_dataset_url,
    select_cols_where_supress_output_is_true,
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_csvw_dsd_qube_components,
    select_dsd_code_list_and_cols,
    select_qb_dataset_url,
)
from csvcubed.cli.inspect.inspectdatasetmanager import (
    get_dataset_observations_info,
    get_dataset_val_counts_info,
    load_csv_to_dataframe,
)
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsInfoResult,
)
from csvcubed.utils.csvdataset import (
    transform_dataset_to_canonical_shape,
)
from csvcubed.models.csvcubedexception import (
    InputTypeIsUnknownException,
    JsonldNotSupportedException,
)


@dataclass
class MetadataPrinter:
    """
    This class produces the printables necessary for producing outputs to the CLI.
    """
    
    csvw_type: CSVWType
    csvw_metadata_rdf_graph: Graph
    csvw_metadata_json_path: Path
    
    dataset_uri: str = field(init=False)
    dsd_uri: str = field(init=False)
    qube_components: List[QubeComponentResult] = field(init=False)
    
    def _get_type_str(self):
        if self.csvw_type == CSVWType.QbDataSet:
            return "data cube"
        elif self.csvw_type == CSVWType.CodeList:
            return "code list"
        else:
            raise InputTypeIsUnknownException()

    @property
    def type_info_printable(self) -> str:
        """
        Generates a printable of metadata type information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if self.csvw_type == CSVWType.QbDataSet:
            return "- This file is a data cube."
        else:
            return "- This file is a code list."

    @property
    def catalog_metadata_printable(self) -> str:
        """
        Generates a printable of catalog metadata (e.g. title, description, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        result: CatalogMetadataResult = select_csvw_catalog_metadata(
            self.csvw_metadata_rdf_graph
        )
        self.dataset_uri = result.dataset_uri

        return f"- The {self._get_type_str()} has the following catalog metadata:{result.output_str}"

    @property
    def dsd_info_printable(self) -> str:
        """
        Generates a printable of Data Structure Definition (DSD) information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        result_dataset_label_dsd_uri: DSDLabelURIResult = (
            select_csvw_dsd_dataset_label_and_dsd_def_uri(self.csvw_metadata_rdf_graph)
        )
        self.dsd_uri = result_dataset_label_dsd_uri.dsd_uri

        result_qube_components: QubeComponentsResult = select_csvw_dsd_qube_components(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )
        self.qube_components = result_qube_components.qube_components

        result_cols_with_suppress_output_true: ColsWithSuppressOutputTrueResult = (
            select_cols_where_supress_output_is_true(self.csvw_metadata_rdf_graph)
        )

        return f"- The {self._get_type_str()} has the following data structure definition:{result_dataset_label_dsd_uri.output_str}{result_qube_components.output_str}{result_cols_with_suppress_output_true.output_str}"

    @property
    def codelist_info_printable(self) -> str:
        """
        Generates a printable of dsd code list information (e.g. column name, type, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """

        result: CodelistsResult = select_dsd_code_list_and_cols(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )

        return f"- The {self._get_type_str()} has the following code list information:{result.output_str}"

    @property
    def dataset_observations_info_printable(self) -> str:
        """
        Generates a printable of top 10 and last 10 records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """

        result_dataset_url: DatasetURLResult
        if self.csvw_type == CSVWType.QbDataSet:
            result_dataset_url = select_qb_dataset_url(
                self.csvw_metadata_rdf_graph, self.dataset_uri
            )
        elif self.csvw_type == CSVWType.CodeList:
            result_dataset_url = select_codelist_dataset_url(
                self.csvw_metadata_rdf_graph
            )
        else:
            raise JsonldNotSupportedException()

        self.dataset: pd.DataFrame = load_csv_to_dataframe(
            self.csvw_metadata_json_path, Path(result_dataset_url.dataset_url)
        )

        result: DatasetObservationsInfoResult = get_dataset_observations_info(
            self.dataset
        )

        return f"- The {self._get_type_str()} has the following dataset information:{result.output_str}"

    @property
    def dataset_val_counts_by_measure_unit_info_printable(self) -> str:
        """
        Generates a printable of dataset value counts broken-down by measure and unit.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        (
            canonical_shape_dataset,
            measure_col,
            unit_col,
        ) = transform_dataset_to_canonical_shape(
            self.dataset,
            self.qube_components,
            self.dsd_uri,
            self.csvw_metadata_rdf_graph,
            self.csvw_metadata_json_path,
        )

        result_val_count = get_dataset_val_counts_info(
            canonical_shape_dataset, measure_col, unit_col
        )
        return f"- The {self._get_type_str()} has the following value counts:{result_val_count.output_str}"
