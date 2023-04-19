"""
Code List Inspector
-------------------

This module contains the `CodeListInspector` class which allows API-style access to information
about code lists contained within an RDF graph.
"""
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from csvcubedmodels.rdf.namespaces import SKOS

from csvcubed.models.sparqlresults import (
    CatalogMetadataResult,
    CodeListTableIdentifers,
    ColumnDefinition,
)
from csvcubed.utils.iterables import first
from csvcubed.utils.pandas import read_csv
from csvcubed.utils.sparql_handler.csvw_inspector import CsvWInspector
from csvcubed.utils.text import truncate
from csvcubed.utils.uri import file_uri_to_path, looks_like_uri
from csvcubed.writers.skoscodelistwriter import (
    LABEL_COL_TITLE,
    URI_IDENTIFIER_COL_TITLE,
)


@dataclass
class CodeListInspector:
    """
    Allows API-style access to information about code lists contained within an RDF graph.
    """

    csvw_inspector: CsvWInspector

    @cached_property
    def _code_list_table_identifiers(self) -> List[CodeListTableIdentifers]:
        """This holds the identifiers mapping between csv_url and the concept_scheme_url."""

        def get_table_identifiers(
            csv_url: str,
            column_definitions: List[ColumnDefinition],
        ) -> Optional[CodeListTableIdentifers]:
            """
            This function checks the column definitions to find columns which place a concept into a scheme (propertyUrl = skos:inScheme)
            and return the revelevant CodeListTableIdentifers.

            In case of more then one a KeyError is returned.
            """
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

        # Get the csv_url -> column_scheme_url identifiers for all csv files.
        table_identifiers = [
            get_table_identifiers(csv_url, columns)
            for (csv_url, columns) in self.csvw_inspector.column_definitions.items()
        ]

        # If the csv file doesn't have a code list in it, don't include it in the code list identifiers returned.
        return [i for i in table_identifiers if i is not None]

    def get_table_identifiers_for_concept_scheme(
        self, concept_scheme_url: str
    ) -> CodeListTableIdentifers:
        """Returns the table identifiers (csv URL & concept scheme URL) for a given concept scheme URL.
        Raises a KeyError if it cannot be found."""
        identifiers = first(
            self._code_list_table_identifiers,
            lambda i: i.concept_scheme_url == concept_scheme_url,
        )

        if identifiers is None:
            raise KeyError(
                f"Could not find code list table identifiers for ConceptScheme URL: '{concept_scheme_url}'"
            )

        return identifiers

    def get_catalog_metadata_for_concept_scheme(
        self, concept_scheme_url: str
    ) -> CatalogMetadataResult:
        """Returns the Catalogue Metadata for a given ConceptScheme. Raises a KeyError if it cannot be found."""
        catalog_mdata_results = self.csvw_inspector.catalog_metadata

        result = first(
            catalog_mdata_results, lambda i: i.dataset_uri == concept_scheme_url
        )

        if result is None:
            raise KeyError(
                f"Can not find Catalogue Meatadata associated with the concept scheme URL '{concept_scheme_url}'."
            )

        return result

    def get_map_code_list_uri_to_label(self, concept_scheme_uri: str) -> Dict[str, str]:
        """
        Maps the code list's Uri Identifiers to human-readable labels
        """
        csv_url = self.get_table_identifiers_for_concept_scheme(
            concept_scheme_uri
        ).csv_url

        if looks_like_uri(csv_url):
            if urlparse(csv_url).scheme == "file":
                # pandas expects local file URLs to be in the format `file://localhost/path/to/table.csv.`
                absolute_csv_url = file_uri_to_path(csv_url)
            else:
                absolute_csv_url = csv_url
        else:
            absolute_csv_url = file_uri_to_path(
                urljoin(self.csvw_inspector.csvw_json_path.as_uri(), csv_url)
            )

        (dataframe, _) = read_csv(
            absolute_csv_url, usecols=[URI_IDENTIFIER_COL_TITLE, LABEL_COL_TITLE]
        )

        duplicated_uris = dataframe[
            dataframe[URI_IDENTIFIER_COL_TITLE].duplicated() == True
        ]
        duplicated_labels = dataframe[dataframe[LABEL_COL_TITLE].duplicated() == True]
        if duplicated_uris.size > 0:
            duplicate_uris: str = truncate(
                ", ".join(duplicated_uris[URI_IDENTIFIER_COL_TITLE]), 50
            )
            raise ValueError(
                f"Duplicate URIs '{duplicate_uris}' in `Uri Identifier` column for {csv_url}"
            )
        elif duplicated_labels.size > 0:
            duplicate_labels: str = truncate(
                ", ".join(duplicated_labels[LABEL_COL_TITLE]), 50
            )
            raise ValueError(
                f"Duplicate labels '{duplicate_labels}' in `Label` column for {csv_url}"
            )

        dict_uri_to_label = dict(
            zip(dataframe[URI_IDENTIFIER_COL_TITLE], dataframe[LABEL_COL_TITLE])
        )

        return dict_uri_to_label

    def get_primary_csv_url(self) -> str:
        """
        Retrieves the csv_url for the primary CSV defined in the CSV-W.
        This will only work if the primary file loaded into the graph was a
        code list.
        """
        primary_catalog_metadata = self.csvw_inspector.get_primary_catalog_metadata()
        return self.get_table_identifiers_for_concept_scheme(
            primary_catalog_metadata.dataset_uri
        ).csv_url
