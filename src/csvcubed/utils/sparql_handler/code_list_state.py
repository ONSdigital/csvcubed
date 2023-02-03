from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional

from csvcubedmodels.rdf.namespaces import SKOS

from csvcubed.models.sparqlresults import CodeListTableIdentifers, ColumnDefinition
from csvcubed.utils.sparql_handler.csvw_state import CsvWState


@dataclass
class CodeListState:
    csvw_state: CsvWState

    @cached_property
    def _code_list_table_identifiers(self) -> List[CodeListTableIdentifers]:
        def get_table_identifiers(
            csv_url: str,
            column_definitions: List[ColumnDefinition],
        ) -> Optional[CodeListTableIdentifers]:
            in_scheme_columns = [
                c
                for c in column_definitions
                if c.property_url == "skos:inScheme"
                or c.property_url == str(SKOS.inScheme)
            ]
            if not any(in_scheme_columns):
                return None

            if len(in_scheme_columns) == 1:
                return CodeListTableIdentifers(csv_url, in_scheme_columns[0].value_url)

            raise KeyError(f"Found multiple skos:inScheme columns in '{csv_url}'.")

        table_identifiers = [
            get_table_identifiers(csv_url, columns)
            for (csv_url, columns) in self.csvw_state.column_definitions.items()
        ]

        return [i for i in table_identifiers if i is not None]

    def link_csv_url_to_concept_scheme_url(self) -> str:
        identifiers = self._code_list_table_identifiers
        csv_url = identifiers[0].csv_url
        concept_scheme_url = identifiers[1].concept_scheme_url

        return concept_scheme_url

    # def get_csvw_catalog_metadata(self, csv_url: str) -> CatalogMetadataResult:
    #     """
    #     todo: Access the stuff from `self.csvw_state.catalog_metadata` and return the relevant value.

    #     When in code_list_state, need a way to link between csv_url and concept scheme (this needs a new query).
    #     Filter catalog metadata results so they represent the one associated with the csv_url. (dataset url = concept scheme url)
    #     """
    #     pass
