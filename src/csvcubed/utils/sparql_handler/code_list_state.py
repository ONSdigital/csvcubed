from dataclasses import dataclass
from functools import cached_property
from typing import List

from csvcubed.models.sparqlresults import ColumnDefinition
from csvcubed.utils.sparql_handler.csvw_state import CsvWState
from csvcubed.utils.sparql_handler.sparqlquerymanager import select_codelist_csv_url


@dataclass
class CodeListState:
    csvw_state: CsvWState

    @cached_property
    def _concept_scheme(self):
        data_set_uri = self.csvw_state.get_primary_catalog_metadata().dataset_uri
        result = select_codelist_csv_url()

    def get_link_for_thing(self) -> List[ColumnDefinition]:

        return self.csvw_state.get_column_definitions_for_csv

    # def get_csvw_catalog_metadata(self, csv_url: str) -> CatalogMetadataResult:
    #     """
    #     todo: Access the stuff from `self.csvw_state.catalog_metadata` and return the relevant value.

    #     When in code_list_state, need a way to link between csv_url and concept scheme (this needs a new query).
    #     Filter catalog metadata results so they represent the one associated with the csv_url. (dataset url = concept scheme url)
    #     """
    #     pass
