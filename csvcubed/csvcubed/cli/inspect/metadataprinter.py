"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

from pathlib import Path
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
    select_unit_col_from_dsd,
)
from csvcubed.cli.inspect.inspectdatasetmanager import (
    DatasetMeasureType,
    DatasetUnitType,
    get_dataset_measure_type,
    get_dataset_observations_info,
    get_dataset_unit_type,
    get_measure_col_from_dsd,
    get_multi_measure_dataset_val_counts_info,
    get_single_measure_dataset_val_counts_info,
    get_single_measure_label_from_dsd,
    get_single_unit_label_from_dsd,
    get_unit_col_from_dsd,
    load_csv_to_dataframe,
)
from csvcubed.models.inspectdataframeresults import (
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.utils.csvdataset import CanonicalShapeRequiredCols

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

    def gen_dataset_val_counts_by_measure_unit_info_printable(self) -> str:
        """
        Generates a printable of dataset value counts broken-down by measure and unit.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        dataset_measure_type = get_dataset_measure_type(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )
        dataset_unit_type = get_dataset_unit_type(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )

        measure_col: str = get_measure_col_from_dsd(
            self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
        )
        unit_col: str
        
        if dataset_unit_type == DatasetUnitType.SINGLE_UNIT:
            unit_col = select_unit_col_from_dsd(
                self.csvw_metadata_rdf_graph, self.dataset_uri
            ).unit_label
        elif dataset_unit_type == DatasetUnitType.MULTI_UNIT:
            unit_col = get_unit_col_from_dsd(
                self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
            )
        else:
            raise Exception("The dataset unit type is unknown.")

        result_val_count: DatasetObservationsByMeasureUnitInfoResult
        if dataset_measure_type == DatasetMeasureType.SINGLE_MEASURE:
            single_measure_label: str = get_single_measure_label_from_dsd(
                self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
            )
            single_unit_label: str = get_single_unit_label_from_dsd(
                self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
            )
            result_val_count = get_single_measure_dataset_val_counts_info(
                self.dataset,
                measure_col,
                unit_col,
                single_measure_label,
                single_unit_label,
            )
        elif dataset_measure_type == DatasetMeasureType.MULTI_MEASURE:
            result_val_count = get_multi_measure_dataset_val_counts_info(
                self.dataset, measure_col, unit_col
            )
        else:
            raise Exception("The dataset measure type is unknown.")

        return f"- The {self._get_type_str()} has the following value counts:{result_val_count.output_str}"
