from dataclasses import dataclass
from functools import cached_property
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, List

import rdflib

from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.sparqlresults import CatalogMetadataResult
from csvcubed.utils.iterables import group_by
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
    select_csvw_catalog_metadata,
)

# map_dsd_uri_to_csv_url = {
#     i.dsd_uri: i.csv_url for i in self._cube_table_identifiers.values()
# }
# return groupby(
#     result.qube_components, lambda c: map_dsd_uri_to_csv_url[c.dsd_uri]
# )
# return group_by(results, lambda r: r.dataset_uri)


@dataclass
class CsvWState:
    rdf_graph: rdflib.ConjunctiveGraph
    primary_graph_uri: str
    csvw_json_path: Path

    @cached_property
    def catalog_metadata(self) -> List[CatalogMetadataResult]:
        """
        Returns a list of catalog metadata results such as title, label, issue/modification date and time etc.
        This supports each result also having the graph_uri that the dcat:Dataset was defined in with it.
        """
        results = select_csvw_catalog_metadata(self.rdf_graph)
        return results

    @cached_property
    def csvw_type(self) -> CSVWType:
        # Need to get the primary graph
        # We currently have the primary graph uri + rdf_graph
        primary_graph = self.rdf_graph.get_context(self.primary_graph_uri)
        if ask_is_csvw_code_list(primary_graph):
            return CSVWType.CodeList
        elif ask_is_csvw_qb_dataset(primary_graph):
            return CSVWType.QbDataSet
        else:
            raise TypeError(
                "The input metadata is invalid as it is not a data cube or a code list."
            )

    def get_primary_catalog_metadata(self) -> CatalogMetadataResult:
        """
        Retrieves the catalog metadata that is specifically only defined in the primary graph.
        """
        for catalog_metadata_result in self.catalog_metadata:
            if catalog_metadata_result.graph_uri == self.primary_graph_uri:
                return catalog_metadata_result

        raise KeyError(
            f"Could not find catalog metadata in primary graph '{self.primary_graph_uri}'."
        )
