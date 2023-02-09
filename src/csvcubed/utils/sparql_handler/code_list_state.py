from dataclasses import dataclass

from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector


@dataclass
class CodeListState:
    csvw_inspector: CsvWInspector

    # def get_csvw_catalog_metadata(self, csv_url: str) -> CatalogMetadataResult:
    #     """
    #     todo: Access the stuff from `self.csvw_inspector.catalog_metadata` and return the relevant value.

    #     When in code_list_state, need a way to link between csv_url and concept scheme (this needs a new query).
    #     Filter catalog metadata results so they represent the one associated with the csv_url. (dataset url = concept scheme url)
    #     """
    #     pass
