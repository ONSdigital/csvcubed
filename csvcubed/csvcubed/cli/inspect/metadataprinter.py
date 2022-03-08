"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

from mailbox import linesep
from pathlib import Path
from csvcubed.models.inspectdataframeresults import DatasetObservationsInfoResult
from csvcubed.utils.printable import get_printable_tabuler_str_from_dataframe
from pandas import DataFrame

from rdflib import Graph, URIRef

from csvcubed.models.inspectsparqlresults import (
    CatalogMetadataResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    DSDLabelURIResult,
    DatasetURLResult,
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
    load_csv_to_dataframe,
)


class MetadataPrinter:
    """
    This class produces the printables necessary for producing outputs to the CLI.
    """

    def __init__(
        self,
        csvw_type: CSVWType,
        csvw_metadata_rdf_graph: Graph,
        csvw_metadata_json_path: Path,
    ):
        self.csvw_type: CSVWType = csvw_type
        self.csvw_metadata_rdf_graph: Graph = csvw_metadata_rdf_graph
        self.csvw_metadata_json_path: Path = csvw_metadata_json_path

    def _get_type_str(self):
        if self.csvw_type == CSVWType.QbDataSet:
            return "data cube"
        elif self.csvw_type == CSVWType.CodeList:
            return "code list"
        else:
            raise Exception("The input type is unknown")

    def gen_type_info_printable(self) -> str:
        """
        Generates a printable of metadata type information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if self.csvw_type == CSVWType.QbDataSet:
            return "- This file is a data cube."
        else:
            return "- This file is a code list."

    def gen_catalog_metadata_printable(self) -> str:
        """
        Generates a printable of catalog metadata (e.g. title, description, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        result: CatalogMetadataResult = select_csvw_catalog_metadata(
            self.csvw_metadata_rdf_graph
        )
        self.dataset_uri: URIRef = result.dataset_uri

        return f"- The {self._get_type_str()} has the following catalog metadata:{result.output_str}"

    def gen_dsd_info_printable(self) -> str:
        """
        Generates a printable of Data Structure Definition (DSD) information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        result_dataset_label_dsd_uri: DSDLabelURIResult = (
            select_csvw_dsd_dataset_label_and_dsd_def_uri(self.csvw_metadata_rdf_graph)
        )
        self.dsd_uri: URIRef = result_dataset_label_dsd_uri.dsd_uri

        result_qube_components: QubeComponentsResult = select_csvw_dsd_qube_components(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )

        result_cols_with_suppress_output_true: ColsWithSuppressOutputTrueResult = (
            select_cols_where_supress_output_is_true(self.csvw_metadata_rdf_graph)
        )

        return f"- The {self._get_type_str()} has the following data structure definition:{result_dataset_label_dsd_uri.output_str}{result_qube_components.output_str}{result_cols_with_suppress_output_true.output_str}"

    def gen_codelist_info_printable(self) -> str:
        """
        Generates a printable of dsd code list information (e.g. column name, type, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """

        result: CodelistsResult = select_dsd_code_list_and_cols(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )

        return f"- The {self._get_type_str()} has the following code list information:{result.output_str}"

    def gen_dataset_observations_info_printable(self) -> str:
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
            raise Exception("The input csvw json-ld is not supported.")
            
        self.dataset: DataFrame = load_csv_to_dataframe(
            self.csvw_metadata_json_path, Path(result_dataset_url.dataset_url)
        )

        result: DatasetObservationsInfoResult = get_dataset_observations_info(
            self.dataset
        )
        return f"- The {self._get_type_str()} has the following dataset information:{result.output_str}"
