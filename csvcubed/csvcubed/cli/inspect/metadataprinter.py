"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""

import json
from pathlib import Path
import dateutil.parser
from typing import List

from rdflib import Graph

from csvcubed.utils.sparql import none_or_map
from csvcubed.utils.qb.components import (
    get_printable_component_property,
    get_printable_component_property_type,
)
from csvcubed.cli.inspect.metadatainputvalidator import CSVWType
from csvcubed.cli.inspect.inspectsparqlqueries import (
    select_cols_w_supress_output,
    select_csvw_dsd_dataset_label_and_dsd_def_uri,
    select_csvw_dsd_qube_components,
    select_csvw_information,
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

    def gen_type_info_printable(self) -> str:
        """
        Generates a printable of metadata type information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if self.csvw_type == CSVWType.QbDataSet:
            return "This file is a data cube."
        else:
            return "This file is a code list."

    def gen_metadata_info_printable(self) -> str:
        """
        Generates a printable of metadata information (e.g. title, description, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """

        result = select_csvw_information(self.csvw_metadata_rdf_graph)
        result_dict = result.asdict()

        return json.dumps(
            {
                "title": result_dict["title"],
                "label": result_dict["label"],
                "issued": dateutil.parser.isoparse(result_dict["issued"]),
                "modified": dateutil.parser.isoparse(result_dict["modified"]),
                "comment": none_or_map(result_dict.get("comment"), str),
                "description": none_or_map(result_dict.get("description"), str),
                "license": none_or_map(result_dict.get("license"), str),
                "creator": none_or_map(result_dict.get("creator"), str),
                "publisher": none_or_map(result_dict.get("publisher"), str),
                "landing_pages": []
                if len(result_dict["landingPages"]) == 0
                else result_dict["landingPages"].split("|"),
                "themes": []
                if len(result_dict["themes"]) == 0 == 0
                else result_dict["themes"].split("|"),
                "keywords": []
                if len(result_dict["keywords"]) == 0
                else result_dict["keywords"].split("|"),
                "contact_point": none_or_map(result_dict.get("contactPoint"), str),
                "identifier": result_dict["identifier"],
            },
            indent=4,
            default=str,
        )

    def gen_dsd_info_printable(self) -> str:
        """
        Generates a printable of Data Structure Definition (DSD) information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if self.csvw_type == CSVWType.CodeList:
            return "N/A"

        result_dataset_label_uri = select_csvw_dsd_dataset_label_and_dsd_def_uri(
            self.csvw_metadata_rdf_graph
        )
        result_dataset_label_uri_dict = result_dataset_label_uri.asdict()
        self.dsd_uri = str(result_dataset_label_uri_dict["dataStructureDefinition"])

        results_qube_components = select_csvw_dsd_qube_components(
            self.csvw_metadata_rdf_graph, self.dsd_uri
        )
        qube_components: List[dict] = list(
            map(
                lambda component: {
                    "componentProperty": get_printable_component_property(
                        component["componentProperty"], self.csvw_metadata_json_path
                    ),
                    "componentPropertyLabel": none_or_map(
                        component.get("componentPropertyLabel"), str
                    ),
                    "componentPropertyType": get_printable_component_property_type(
                        component["componentPropertyType"]
                    ),
                    "csvColumnTitle": none_or_map(component.get("csvColumnTitle"), str),
                    "required": component["required"],
                },
                results_qube_components,
            )
        )

        results_cols_with_suppress_output = select_cols_w_supress_output(
            self.csvw_metadata_rdf_graph
        )

        return json.dumps(
            {
                "dataset_label": result_dataset_label_uri_dict["dataSetLabel"],
                "num_of_components": len(qube_components),
                "components": qube_components,
                "columns_with_suppress_output_true": results_cols_with_suppress_output,
            },
            indent=4,
            default=str,
        )

    def gen_codelist_info_printable(self) -> str:
        """
        Generates a printable of code list information (e.g. column name, type, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read codelist info using Pandas and generate CLI printable"""
        return ""

    def gen_headtail_printable(self) -> str:
        """
        Generates a printable of top 10 and last 10 records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read head/tail using Pandas and generate CLI printable"""
        # Check panda.to_string() and panda.to_text() cmds and other printable functions in pandas.
        return ""

    def gen_valcount_printable(self) -> str:
        """
        Generates a printable of number of records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read value count using Pandas and generate CLI printable"""
        # Check panda.to_string() and panda.to_text() cmds and other printable functions in pandas.
        return ""
