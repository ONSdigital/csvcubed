from dataclasses import dataclass
from functools import cached_property
from itertools import groupby
from pathlib import Path
from typing import Dict, List, Any

import rdflib

from csvcubed.models.sparqlresults import CatalogMetadataResult
from csvcubed.utils.iterables import group_by
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
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
    rdf_graph: rdflib.Graph
    primary_graph_uri: str

    @cached_property
    def catalog_metadata(self) -> List[CatalogMetadataResult]:
        """
        TODO: Need to refactor select_csvw_catalog_metadata so it now supports returning a list of results
          where each result has the graph_uri that the dcat:Dataset was defined in with it.
        """
        results = select_csvw_catalog_metadata(self.rdf_graph)
        return results


    def get_primary_catalog_metadata(self) -> CatalogMetadataResult:
        """
        TODO: Get **just** the catalog metadata defined in the primary graph
        """
        
        primary_catalog_metadata = self.catalog_metadata
        return primary_catalog_metadata