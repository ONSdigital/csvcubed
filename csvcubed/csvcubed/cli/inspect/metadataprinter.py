"""
Metadata Printer
----------------

Provides functionality for validating and detecting input metadata.json file.
"""


from csvcubed.cli.inspect.metadatainputhandler import MetadataType
from rdflib import Graph
import pandas as pd


class MetadataPrinter:
    """
    This class produces the printables necessary for producing outputs to the CLI.
    """

    def __init__(self, metadata_rdf_graph: Graph):
        self.metadata_rdf_graph = metadata_rdf_graph

    def gen_type_info_printable(self, metadata_type: MetadataType) -> str:
        """
        Generates a printable of metadata type information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        if metadata_type == MetadataType.DataCube:
            return "This is a data cube."
        else:
            return "This is a code list."

    def gen_metadata_info_printable(self) -> str:
        """
        Generates a printable of metadata information (e.g. title, description, etc.).

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read metadata info using Pandas and generate CLI printable"""
        return ""

    def gen_dsd_info_printable(self) -> str:
        """
        Generates a printable of Data Structure Definition (DSD) information.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read metadata info using Pandas and generate CLI printable"""
        return ""

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
        return ""

    def gen_valcount_printable(self) -> str:
        """
        Generates a printable of number of records.

        Member of :class:`./MetadataPrinter`.

        :return: `str` - user-friendly string which will be output to CLI.
        """
        """TODO: Read value count using Pandas and generate CLI printable"""
        return ""
