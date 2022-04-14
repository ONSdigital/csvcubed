"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple
from pandas import DataFrame

from rdflib import Graph

from csvcubed.models.inspectsparqlresults import (
    CatalogMetadataResult,
    CodeListColsByDatasetUrlResult,
    CodelistColumnResult,
    CodelistsResult,
    ColsWithSuppressOutputTrueResult,
    DSDLabelURIResult,
    QubeComponentsResult,
)
from csvcubed.cli.inspect.metadatainputvalidator import CSVWType
from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_codelist_cols_by_dataset_url,
    select_codelist_dataset_url,
    select_cols_where_supress_output_is_true,
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_csvw_dsd_qube_components,
    select_dsd_code_list_and_cols,
    select_qb_dataset_url,
)
from csvcubed.cli.inspect.inspectdatasetmanager import (
    get_concepts_hierarchy_info,
    get_dataset_observations_info,
    get_dataset_val_counts_info,
    load_csv_to_dataframe,
)
from csvcubed.models.inspectdataframeresults import (
    CodelistHierarchyInfoResult,
    DatasetObservationsByMeasureUnitInfoResult,
    DatasetObservationsInfoResult,
)
from csvcubed.utils.csvdataset import (
    transform_dataset_to_canonical_shape,
)
from csvcubed.models.csvcubedexception import (
    InputNotSupportedException,
)
from csvcubed.utils.skos.codelist import (
    CodelistPropertyUrl,
    get_codelist_col_title_by_property_url,
)


@dataclass
class MetadataPrinter:
    """
    This class produces the printables necessary for producing outputs to the CLI.
    """

    csvw_type: CSVWType
    csvw_metadata_rdf_graph: Graph
    csvw_metadata_json_path: Path

    csvw_type_str: str = field(init=False)
    dataset_url: str = field(init=False)
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
    result_code_list_cols: CodeListColsByDatasetUrlResult = field(init=False)
    result_concepts_hierachy_info: CodelistHierarchyInfoResult = field(init=False)

    @staticmethod
    def get_csvw_type_str(csvw_type: CSVWType) -> str:
        if csvw_type == CSVWType.QbDataSet:
            return "data cube"
        elif csvw_type == CSVWType.CodeList:
            return "code list"
        else:
            raise InputNotSupportedException()

    @staticmethod
    def get_dataset_url(
        csvw_metadata_rdf_graph: Graph,
        csvw_type: CSVWType,
        dataset_uri: str,
    ) -> str:
        if csvw_type == CSVWType.QbDataSet:
            return select_qb_dataset_url(
                csvw_metadata_rdf_graph, dataset_uri
            ).dataset_url
        elif csvw_type == CSVWType.CodeList:
            return select_codelist_dataset_url(csvw_metadata_rdf_graph).dataset_url
        else:
            raise InputNotSupportedException()

    @staticmethod
    def get_parent_label_notation_col_names(
        columns: List[CodelistColumnResult],
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        parent_notation_col_name = get_codelist_col_title_by_property_url(
            columns, CodelistPropertyUrl.SkosBroader
        )
        label_col_name = get_codelist_col_title_by_property_url(
            columns, CodelistPropertyUrl.RDFLabel
        )
        notation_col_name = get_codelist_col_title_by_property_url(
            columns, CodelistPropertyUrl.SkosNotation
        )
        return (parent_notation_col_name, label_col_name, notation_col_name)

    def generate_general_results(self):
        """
        Generates results related to data cubes and code lists.

        Member of :class:`./MetadataPrinter`.
        """
        self.csvw_type_str = self.get_csvw_type_str(self.csvw_type)
        self.result_catalog_metadata = select_csvw_catalog_metadata(
            self.csvw_metadata_rdf_graph
        )
        self.dataset_url = self.get_dataset_url(
            self.csvw_metadata_rdf_graph,
            self.csvw_type,
            self.result_catalog_metadata.dataset_uri,
        )
        self.dataset = load_csv_to_dataframe(
            self.csvw_metadata_json_path, Path(self.dataset_url)
        )
        self.result_dataset_observations_info = get_dataset_observations_info(
            self.dataset, self.csvw_type
        )

    def get_datacube_results(self):
        """
        Generates results specific to data cubes.

        Member of :class:`./MetadataPrinter`.
        """
        self.result_dataset_label_dsd_uri = (
            select_csvw_dsd_dataset_label_and_dsd_def_uri(self.csvw_metadata_rdf_graph)
        )
        self.result_qube_components = select_csvw_dsd_qube_components(
            self.csvw_metadata_rdf_graph,
            self.result_dataset_label_dsd_uri.dsd_uri,
            self.csvw_metadata_json_path,
        )
        self.result_cols_with_suppress_output_true = (
            select_cols_where_supress_output_is_true(self.csvw_metadata_rdf_graph)
        )
        self.result_code_lists = select_dsd_code_list_and_cols(
            self.csvw_metadata_rdf_graph,
            self.result_dataset_label_dsd_uri.dsd_uri,
            self.csvw_metadata_json_path,
        )
        (
            canonical_shape_dataset,
            measure_col,
            unit_col,
        ) = transform_dataset_to_canonical_shape(
            self.dataset,
            self.result_qube_components.qube_components,
            self.result_dataset_label_dsd_uri.dsd_uri,
            self.csvw_metadata_rdf_graph,
            self.csvw_metadata_json_path,
        )
        self.result_dataset_value_counts = get_dataset_val_counts_info(
            canonical_shape_dataset, measure_col, unit_col
        )

    def generate_codelist_results(self):
        """
        Generates results specific to code lists.

        Member of :class:`./MetadataPrinter`.
        """
        self.result_code_list_cols = select_codelist_cols_by_dataset_url(
            self.csvw_metadata_rdf_graph, self.dataset_url
        )
        (
            parent_notation_col_name,
            label_col_name,
            notation_col_name,
        ) = self.get_parent_label_notation_col_names(self.result_code_list_cols.columns)
        self.result_concepts_hierachy_info = get_concepts_hierarchy_info(
            self.dataset, parent_notation_col_name, label_col_name, notation_col_name
        )

    def __post_init__(self):
        self.generate_general_results()

        if self.csvw_type == CSVWType.QbDataSet:
            self.get_datacube_results()
        elif self.csvw_type == CSVWType.CodeList:
            self.generate_codelist_results()

    @property
    def type_info_printable(self) -> str:
        """
        Returns a printable of file content type.

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
