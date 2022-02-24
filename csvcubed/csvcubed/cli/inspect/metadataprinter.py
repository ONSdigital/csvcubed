"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

import json
from pathlib import Path
import dateutil.parser
from typing import Dict, List
import pandas as pd

from rdflib import Graph

from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.qb.components import (
    get_printable_component_property,
    get_printable_component_property_type,
)
from csvcubed.cli.inspect.metadatainputvalidator import CSVWType
from csvcubed.cli.inspect.inspectsparqlmanager import (
    select_cols_w_supress_output,
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
        return "data cube" if self.csvw_type == CSVWType.QbDataSet else "code list"

    def _get_printable_list_str(self, items: List) -> str:
        if len(items) == 0 or len(items[0]) == 0:
            return "None"

        output_str = ""
        for item in items:
            output_str = f"{output_str}\n\t\t-- {item}"
        return output_str

    def _get_printable_tabular_list_str(self, items: List) -> str:
        if len(items) == 0 or len(items[0]) == 0:
            return "None"

        output_str = ""
        for idx, item in enumerate(items):
            output_str = f"{output_str}{item}{',' if idx != len(items)-1 else ''}"
        return output_str

    def _get_printable_tabular_str(self, items: List[Dict], column_names) -> str:
        if len(items) == 0:
            return "None"

        df = pd.DataFrame(items)
        df.columns = column_names
        output_str = df.to_string(index=False)
        if output_str:
            return output_str
        raise Exception("Failed to covert data frame to string")

    def gen_type_info_printable(self) -> str:
        """
        Generates a printable of metadata type information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if self.csvw_type == CSVWType.QbDataSet:
            return "\u2022 This file is a data cube."
        else:
            return "\u2022 This file is a code list."

    def gen_catalog_metadata_printable(self) -> str:
        """
        Generates a printable of catalog metadata (e.g. title, description, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """

        result = select_csvw_catalog_metadata(self.csvw_metadata_rdf_graph)
        result_dict = result.asdict()

        output_str = "\t- Title: {}\n\t- Label: {}\n\t- Issued: {}\n\t- Modified: {}\n\t- License: {}\n\t- Creator: {}\n\t- Publisher: {}\n\t- Landing Pages: {}\n\t- Themes: {}\n\t- Keywords: {}\n\t- Contact Point: {}\n\t- Identifier: {}\n\t- Comment: {}\n\t- Description: {}".format(
            result_dict["title"],
            result_dict["label"],
            result_dict["issued"],
            result_dict["modified"],
            none_or_map(result_dict.get("license"), str),
            none_or_map(result_dict.get("creator"), str),
            none_or_map(result_dict.get("publisher"), str),
            self._get_printable_list_str(str(result_dict["landingPages"]).split("|")),
            self._get_printable_list_str(str(result_dict["themes"]).split("|")),
            self._get_printable_list_str(str(result_dict["keywords"]).split("|")),
            none_or_map(result_dict.get("contact_point"), str),
            result_dict["identifier"],
            none_or_map(result_dict.get("comment"), str),
            str(none_or_map(result_dict.get("description"), str)).replace(
                "\n", "\n\t\t"
            ),
        )

        return f"\u2022 The {self._get_type_str()} has the following catalog metadata:\n {output_str}"

    def gen_dsd_info_printable(self) -> str:
        """
        Generates a printable of Data Structure Definition (DSD) information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        result_dataset_label_uri = select_csvw_dsd_dataset_label_and_dsd_def_uri(
            self.csvw_metadata_rdf_graph
        )
        result_dataset_label_uri_dict = result_dataset_label_uri.asdict()
        self.dsd_uri = str(result_dataset_label_uri_dict["dataStructureDefinition"])
        print(self.dsd_uri)
        
        results_qube_components = select_csvw_dsd_qube_components(
            self.csvw_metadata_rdf_graph, self.dsd_uri
        )

        qube_components: List[Dict] = list(
            map(
                lambda component: {
                    "componentProperty": get_printable_component_property(
                        self.csvw_metadata_json_path,
                        component["componentProperty"],
                    ),
                    "componentPropertyLabel": none_or_map(
                        component.get("componentPropertyLabel"), str
                    )
                    or "",
                    "componentPropertyType": get_printable_component_property_type(
                        str(component["componentPropertyType"]) or ""
                    ),
                    "csvColumnTitle": none_or_map(component.get("csvColumnTitle"), str)
                    or "",
                    "required": ""
                    if component["required"] is None
                    else str(component["required"]),
                },
                results_qube_components,
            )
        )

        results_cols_with_suppress_output = select_cols_w_supress_output(
            self.csvw_metadata_rdf_graph
        )
        cols_with_suppress_output = list(
            map(
                lambda result: str(result["csvColumnTitle"]),
                results_cols_with_suppress_output,
            )
        )

        output_str = "\t- Dataset label: {}\n\t- Columns with suppress output: {}\n\t- Number of components: {}\n\t- Components:\n{}".format(
            result_dataset_label_uri_dict["dataSetLabel"],
            self._get_printable_list_str(cols_with_suppress_output),
            len(qube_components),
            self._get_printable_tabular_str(
                qube_components,
                column_names=[
                    "Property",
                    "Property Label",
                    "Property Type",
                    "Column Title",
                    "Required",
                ],
            ),
        )

        return f"\u2022 The {self._get_type_str()} has the following data structure definition:\n {output_str}"

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
        return f"\u2022 The {self._get_type_str()} has the following code lists:\n {output_str}"

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
