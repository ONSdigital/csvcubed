"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

from pathlib import Path
from typing import Dict, List
from csvcubed.models.cli.inspect.inspectsparqlresults import (
    CatalogMetadataSparqlResult,
    DSDLabelURISparqlResult,
    QubeComponentsSparqlResult,
)
from numpy import sort
import pandas as pd

from rdflib import Graph

from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.qb.components import (
    get_printable_component_property,
    get_printable_component_property_type,
)
from csvcubed.cli.inspect.metadatainputvalidator import CSVWType
from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_cols_where_supress_output_is_true,
    select_csvw_catalog_metadata,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_csvw_dsd_qube_components,
    select_dsd_code_list_and_cols,
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
        result: CatalogMetadataSparqlResult = select_csvw_catalog_metadata(
            self.csvw_metadata_rdf_graph
        )
        return f"- The {self._get_type_str()} has the following catalog metadata:{result.output_str}"

    def gen_dsd_info_printable(self) -> str:
        """
        Generates a printable of Data Structure Definition (DSD) information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        result_dataset_label_dsd_uri: DSDLabelURISparqlResult = (
            select_csvw_dsd_dataset_label_and_dsd_def_uri(self.csvw_metadata_rdf_graph)
        )
        self.dsd_uri = result_dataset_label_dsd_uri.dsd_uri

        result_qube_components: QubeComponentsSparqlResult = (
            select_csvw_dsd_qube_components(
                self.csvw_metadata_rdf_graph, self.dsd_uri, self.csvw_metadata_json_path
            )
        )

        result_cols_with_suppress_output = select_cols_where_supress_output_is_true(
            self.csvw_metadata_rdf_graph
        )

        return f"- The {self._get_type_str()} has the following data structure definition:{result_dataset_label_dsd_uri.output_str}{result_qube_components.output_str}{result_cols_with_suppress_output.output_str}"

    def gen_codelist_info_printable(self) -> str:
        """
        Generates a printable of dsd code list information (e.g. column name, type, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """

        results = select_dsd_code_list_and_cols(
            self.csvw_metadata_rdf_graph, self.dsd_uri
        )
        code_lists: List[Dict] = list(
            map(
                lambda code_list: {
                    "codeList": get_printable_component_property(
                        self.csvw_metadata_json_path,
                        code_list["codeList"],
                    ),
                    "codeListLabel": none_or_map(code_list.get("codeListLabel"), str)
                    or "",
                    "csvColumnsUsedIn": self._get_printable_tabular_list_str(
                        str(code_list["csvColumnsUsedIn"]).split("|")
                    ),
                },
                results,
            )
        )

        output_str = self._get_printable_tabular_str(
            code_lists,
            column_names=["Code List", "Code List Label", "Columns Used In"],
        )
        return (
            f"- The {self._get_type_str()} has the following code lists:\n {output_str}"
        )

    def gen_head_tail_printable(self) -> str:
        """
        Generates a printable of top 10 and last 10 records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read head/tail using Pandas and generate CLI printable"""
        # Check panda.to_string() and panda.to_text() cmds and other printable functions in pandas.
        return ""

    def gen_val_count_printable(self) -> str:
        """
        Generates a printable of number of records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read value count using Pandas and generate CLI printable"""
        return ""
