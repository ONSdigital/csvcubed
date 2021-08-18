"""
CodeList Writer
---------------

Write `NewQbCodeList`s to CSV-Ws as `skos:ConceptScheme` s with DCAT2 metadata.
"""
import datetime
import json
from pathlib import Path
from typing import Tuple
import pandas as pd

from csvqb.models.cube.qb.components.arbitraryrdf import RdfSerialisationHint
from csvqb.models.cube.qb.components.codelist import NewQbCodeList
from csvqb.utils.dict import rdf_resource_to_json_ld
from csvqb.models.rdf.conceptschemeincatalog import ConceptSchemeInCatalog
from csvqb.writers.writerbase import WriterBase

CODE_LIST_NOTATION_COLUMN_NAME = "notation"


class SkosCodeListWriter(WriterBase):
    def __init__(self, new_code_list: NewQbCodeList):
        self.csv_file_name = f"{new_code_list.metadata.uri_safe_identifier}.csv"
        self.new_code_list: NewQbCodeList = new_code_list

    def write(self, output_directory: Path) -> None:
        csv_file_path = (output_directory / self.csv_file_name).absolute()
        metadata_file_path = (
            output_directory / f"{self.csv_file_name}-metadata.json"
        ).absolute()
        table_json_schema_file_path = (
            output_directory
            / f"{self.new_code_list.metadata.uri_safe_identifier}.table.json"
        ).absolute()

        csvw_metadata = self._get_csvw_metadata()
        table_schema = self._get_csvw_table_schema()
        data = self._get_code_list_data()

        with open(str(metadata_file_path), "w+") as f:
            json.dump(csvw_metadata, f, indent=4)

        with open(str(table_json_schema_file_path), "w+") as f:
            json.dump(table_schema, f, indent=4)

        data.to_csv(str(csv_file_path), index=False)

    def _doc_rel_uri(self, fragment: str) -> str:
        """
        URIs declared in the `columns` section of the CSV-W are relative to the CSV's location.
        URIs declared in the JSON-LD metadata section of the CSV-W are relative to the metadata file's location.

        This function makes both point to the same base location - the CSV file's location. This ensures that we
        can talk about the same resources in the `columns` section and the JSON-LD metadata section.
        """
        return f"./{self.csv_file_name}#{fragment}"

    def _get_csvw_table_schema(self) -> dict:
        concept_base_uri = self._doc_rel_uri(
            f"concept/{self.new_code_list.metadata.uri_safe_identifier}/"
        )

        csvw_columns = [
            {
                "titles": "Label",
                "name": "label",
                "required": True,
                "propertyUrl": "rdfs:label",
            },
            {
                "titles": "Notation",
                "name": CODE_LIST_NOTATION_COLUMN_NAME,
                "required": True,
                "propertyUrl": "skos:notation",
            },
            {
                "titles": "Parent Notation",
                "name": "parent_notation",
                "required": False,
                "propertyUrl": "skos:broader",
                "valueUrl": concept_base_uri + "{+parent_notation}",
            },
            {
                "titles": "Sort Priority",
                "name": "sort_priority",
                "required": False,
                "datatype": "integer",
                "propertyUrl": "http://www.w3.org/ns/ui#sortPriority",
            },
            {
                "titles": "Description",
                "name": "description",
                "required": False,
                "propertyUrl": "rdfs:comment",
            },
            {
                "virtual": True,
                "name": "virt_inScheme",
                "required": False,
                "propertyUrl": "skos:inScheme",
                "valueUrl": self._get_concept_scheme_uri(),
            },
        ]

        return {
            "columns": csvw_columns,
            "aboutUrl": concept_base_uri + "{+notation}",
            "primaryKey": CODE_LIST_NOTATION_COLUMN_NAME,
        }

    def _get_concept_scheme_uri(self) -> str:
        return self._doc_rel_uri(
            f"scheme/{self.new_code_list.metadata.uri_safe_identifier}"
        )

    def _get_csvw_metadata(self) -> dict:
        scheme_uri = self._get_concept_scheme_uri()
        additional_metadata = self._get_catalog_metadata(scheme_uri)

        return {
            "@context": "http://www.w3.org/ns/csvw",
            "@id": scheme_uri,
            "url": self.csv_file_name,
            "tableSchema": f"{self.new_code_list.metadata.uri_safe_identifier}.table.json",
            "rdfs:seeAlso": rdf_resource_to_json_ld(additional_metadata),
        }

    def _get_catalog_metadata(self, scheme_uri: str) -> ConceptSchemeInCatalog:
        concept_scheme_with_metadata = ConceptSchemeInCatalog(scheme_uri)
        self.new_code_list.metadata.configure_dcat_dataset(concept_scheme_with_metadata)
        self.new_code_list.copy_arbitrary_triple_fragments_to_resources(
            {
                RdfSerialisationHint.CatalogDataset: concept_scheme_with_metadata,
                RdfSerialisationHint.ConceptScheme: concept_scheme_with_metadata,
            }
        )
        return concept_scheme_with_metadata

    def _get_code_list_data(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Label": [c.label for c in self.new_code_list.concepts],
                "Notation": [c.code for c in self.new_code_list.concepts],
                "Parent Notation": [c.parent_code for c in self.new_code_list.concepts],
                "Sort Priority": [
                    c.sort_order or i for i, c in enumerate(self.new_code_list.concepts)
                ],
                "Description": [c.description for c in self.new_code_list.concepts],
            }
        )
