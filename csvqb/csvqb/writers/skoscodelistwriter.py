"""
    Write `NewQbCodeList`s to CSV-Ws as `skos:ConceptScheme`s with DCAT2 metadata.
"""
import datetime
import json
from pathlib import Path
from typing import Tuple
import pandas as pd


from csvqb.models.cube.csvqb.components.codelist import NewQbCodeList
from csvqb.utils.dict import rdf_resource_to_json_ld_dict
from csvqb.models.rdf.conceptschemeincatalog import ConceptSchemeInCatalog
from csvqb.writers.writerbase import WriterBase


class SkosCodeListWriter(WriterBase):

    def __init__(self, new_code_list: NewQbCodeList):
        self.csv_file_name = f"{new_code_list.metadata.uri_safe_identifier}.csv"
        self.new_code_list: NewQbCodeList = new_code_list

    def write(self, output_directory: Path) -> None:
        csv_file_path = (output_directory / self.csv_file_name).absolute()
        metadata_file_path = (output_directory / f"{self.csv_file_name}-metadata.json").absolute()

        csvw_metadata, data = self._new_code_list_to_csvw_parts()

        with open(str(metadata_file_path), "w+") as f:
            json.dump(csvw_metadata, f, indent=4)

        data.to_csv(str(csv_file_path), index=False)

    def _doc_rel_uri(self, fragment: str) -> str:
        """
            URIs declared in the `columns` section of the CSV-W are relative to the CSV's location.
            URIs declared in the JSON-LD metadata section of the CSV-W are relative to the metadata file's location.

            This function makes both point to the same base location - the CSV file's location. This ensures that we
            can talk about the same resources in the `columns` section and the JSON-LD metadata section.
        """
        return f"./{self.csv_file_name}#{fragment}"

    def _new_code_list_to_csvw_parts(self) -> Tuple[dict, pd.DataFrame]:
        csvw_metadata = self._get_csvw_metadata()
        data = self._get_code_list_data()

        return csvw_metadata, data

    def _get_csvw_metadata(self, ) -> dict:
        additional_metadata = self._get_catalog_metadata()

        csvw_columns = [
            {
                "titles": "Label",
                "name": "label",
                "required": True,
                "propertyUrl": "rdfs:label"
            },
            {
                "titles": "Notation",
                "name": "notation",
                "required": True,
                "propertyUrl": "skos:notation"
            },
            {
                "titles": "Parent Notation",
                "name": "parent_notation",
                "required": False,
                "propertyUrl": "skos:broader",
                "valueUrl": self._doc_rel_uri("concept/{+parent_notation}")
            },
            {
                "titles": "Sort Priority",
                "name": "sort_priority",
                "required": False,
                "datatype": "integer",
                "propertyUrl": "http://www.w3.org/ns/ui#sortPriority"
            },
            {
                "titles": "Description",
                "name": "description",
                "required": False,
                "propertyUrl": "rdfs:comment"
            },
            {
                "virtual": True,
                "name": "virt_inScheme",
                "required": False,
                "propertyUrl": "skos:inScheme",
                "valueUrl": self._doc_rel_uri("scheme")
            }
        ]

        csvw_metadata = {
            "@context": "http://www.w3.org/ns/csvw",
            "@id": self._doc_rel_uri("scheme"),
            "url": self.csv_file_name,
            "tableSchema": {
                "columns": csvw_columns,
                "aboutUrl": self._doc_rel_uri("concept/{+notation}")
            },
            "rdfs:seeAlso": rdf_resource_to_json_ld_dict(additional_metadata)
        }

        return csvw_metadata

    def _get_catalog_metadata(self) -> ConceptSchemeInCatalog:
        dt_now = datetime.datetime.now()
        metadata = self.new_code_list.metadata

        concept_scheme = ConceptSchemeInCatalog(self._doc_rel_uri("scheme"))
        concept_scheme.label = concept_scheme.title = metadata.title
        concept_scheme.issued = metadata.issued or dt_now
        concept_scheme.modified = dt_now
        concept_scheme.comment = metadata.summary
        concept_scheme.description = metadata.description
        concept_scheme.license = metadata.license_uri
        concept_scheme.publisher = metadata.publisher_uri
        concept_scheme.landing_page = metadata.landing_page_uri
        concept_scheme.themes = set(metadata.theme_uris)
        concept_scheme.keywords = set(metadata.keywords)

        return concept_scheme

    def _get_code_list_data(self) -> pd.DataFrame:
        return pd.DataFrame({
            "Label": [c.label for c in self.new_code_list.concepts],
            "Notation": [c.code for c in self.new_code_list.concepts],
            "Parent Notation": [c.parent_code for c in self.new_code_list.concepts],
            "Sort Priority": [c.sort_order or i for i, c in enumerate(self.new_code_list.concepts)],
            "Description": [c.description for c in self.new_code_list.concepts]
        })
