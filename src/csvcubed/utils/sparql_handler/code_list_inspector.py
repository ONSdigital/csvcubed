"""
Code List Inspector
-------------------

This is the CodeListInspector class script, which is an API class that allows to access information.
"""
from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional

from csvcubedmodels.rdf.namespaces import SKOS

from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodeListTableIdentifers,
    ColumnDefinition,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.sparql_handler.csvw_state import CsvWState


@dataclass
class CodeListInspector:
    """The API interface for the codelist information, allowing to access information."""

    csvw_state: CsvWState

    @cached_property
    def _code_list_table_identifiers(self) -> List[CodeListTableIdentifers]:
        """This funciton gets the csv_url and columndefinition and calls get_table_identifiers which returns the CodeListTableIdentifers thats property_url is
        (skos:inScheme)."""

        def get_table_identifiers(
            csv_url: str,
            column_definitions: List[ColumnDefinition],
        ) -> Optional[CodeListTableIdentifers]:
            """This function checks the column definitions for (skos:inScheme) and return the revelevant CodeListTableIdentifers.
            In case of more then one a KeyError is returned."""
            in_scheme_columns = [
                c
                for c in column_definitions
                if c.property_url == "skos:inScheme"
                or c.property_url == str(SKOS.inScheme)
            ]
            if not any(in_scheme_columns):
                return None

            if len(in_scheme_columns) == 1:
                return CodeListTableIdentifers(
                    csv_url, str(in_scheme_columns[0].value_url)
                )

            raise KeyError(f"Found multiple skos:inScheme columns in '{csv_url}'.")

        table_identifiers = [
            get_table_identifiers(csv_url, columns)
            for (csv_url, columns) in self.csvw_state.column_definitions.items()
        ]

        return [i for i in table_identifiers if i is not None]

    def get_table_identifiers_for_concept_scheme(
        self, concept_scheme_url: str
    ) -> CodeListTableIdentifers:
        """This function check the CodeListTableIdentifers and returns the value thats concept_scheme_url mathces with the given argument."""
        identifiers = first(
            self._code_list_table_identifiers,
            lambda i: i.concept_scheme_url == concept_scheme_url,
        )

        if identifiers is None:
            raise KeyError(
                f"Could not find code list table identifiers for ConceptScheme URL: '{concept_scheme_url}'"
            )

        return identifiers

    def get_csvw_catalog_metadata(self) -> CatalogMetadataResult:
        """This function will access the catalogmetadataResult and compares the concept_sceme_url and returns the relevant value"""
        catalog_mdata_results = self.csvw_state.catalog_metadata

        concept_scheme_url = self._code_list_table_identifiers[0].concept_scheme_url

        for result in catalog_mdata_results:
            if result.dataset_uri == concept_scheme_url:
                return result

        raise ValueError(
            f"None of the results can be associated with the {concept_scheme_url}"
        )
