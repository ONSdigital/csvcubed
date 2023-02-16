from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List

import rdflib

from csvcubed.models.csvwtype import CSVWType
from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    PrimaryKeyColNamesByDatasetUrlResult,
    TableSchemaPropertiesResult,
    TableSchemaPropertiesResults,
)
from csvcubed.utils.dict import get_from_dict_ensure_exists
from csvcubed.utils.sparql_handler.sparql import path_to_file_uri_for_rdflib
from csvcubed.utils.sparql_handler.sparqlquerymanager import (
    ask_is_csvw_code_list,
    ask_is_csvw_qb_dataset,
    select_csvw_catalog_metadata,
    select_primary_key_col_names_by_csv_url,
    select_table_schema_properties,
)


@dataclass
class CsvWInspector:
    rdf_graph: rdflib.ConjunctiveGraph
    csvw_json_path: Path

    primary_graph_uri: str = field(init=False)

    def __post_init__(self):
        self.primary_graph_uri = path_to_file_uri_for_rdflib(self.csvw_json_path)

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
        primary_graph = self.rdf_graph.get_context(self.primary_graph_uri)
        if ask_is_csvw_code_list(primary_graph):
            return CSVWType.CodeList
        elif ask_is_csvw_qb_dataset(primary_graph):
            return CSVWType.QbDataSet
        else:
            raise TypeError(
                "The input metadata is invalid as it is not a data cube or a code list."
            )

    @cached_property
    def _table_schema_properties(self) -> Dict[str, TableSchemaPropertiesResults]:
        """
        Cached property for the select_table_schema_properties query that stores the query's results.
        """
        results = select_table_schema_properties(self.rdf_graph)
        # results_dict: Dict[str, TableSchemaPropertiesResult] = {}
        # for result in results:
        #     results_dict[result.csv_url] = result

        return results

    @cached_property
    def _primary_key_by_csv_url(self) -> PrimaryKeyColNamesByDatasetUrlResult:
        """
        Cached property for the select_primary_key_col_names_by_csv_url query that stores the query's results.
        """
        csv_url: str
        result = select_primary_key_col_names_by_csv_url(
            self.rdf_graph, self.get_table_schema_properties().table_url
        )

        return result

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

    def get_table_schema_properties(self) -> TableSchemaPropertiesResults:
        """
        Retrieves the stored result of the table schema properties cached property.
        """
        str_for_input = self._table_schema_properties.keys()
        keys = list(str_for_input)
        result: TableSchemaPropertiesResults = get_from_dict_ensure_exists(
            self._table_schema_properties, keys[0]
        )
        return result

    def get_primary_key_by_csv_url(
        self,
    ) -> PrimaryKeyColNamesByDatasetUrlResult:
        """
        Retrieves the stored result from the codelist priary key by csv url cached property.
        """
        return self._primary_key_by_csv_url
