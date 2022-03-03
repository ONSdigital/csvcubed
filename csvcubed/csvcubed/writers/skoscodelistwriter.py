"""
CodeList Writer
---------------

Write `NewQbCodeList`s to CSV-Ws as `skos:ConceptScheme` s with DCAT2 metadata.
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
from csvcubedmodels.rdf import ExistingResource

from csvcubed.models.cube.qb.components import (
    RdfSerialisationHint,
    NewQbCodeList,
    CompositeQbCodeList,
)
from csvcubed.utils.dict import rdf_resource_to_json_ld
from csvcubed.models.rdf.conceptschemeincatalog import ConceptSchemeInCatalog
from csvcubed.writers.urihelpers.skoscodelist import SkosCodeListNewUriHelper
from csvcubed.writers.writerbase import WriterBase

CODE_LIST_NOTATION_COLUMN_NAME = "notation"

_logger = logging.getLogger(__name__)


@dataclass
class SkosCodeListWriter(WriterBase):
    new_code_list: NewQbCodeList
    csv_file_name: str = field(init=False)
    _new_uri_helper: SkosCodeListNewUriHelper = field(init=False)

    def __post_init__(self):
        self.csv_file_name = f"{self.new_code_list.metadata.uri_safe_identifier}.csv"
        _logger.debug(
            "Initialising %s with CSV output set to '%s'",
            SkosCodeListWriter.__name__,
            self.csv_file_name,
        )
        self._new_uri_helper = SkosCodeListNewUriHelper(self.new_code_list)

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
            _logger.debug("Writing CSV-W JSON-LD to %s", metadata_file_path)
            json.dump(csvw_metadata, f, indent=4)

        with open(str(table_json_schema_file_path), "w+") as f:
            _logger.debug(
                "Writing CSV-W table schema to %s", table_json_schema_file_path
            )
            json.dump(table_schema, f, indent=4)

        _logger.debug("Writing CSV to %s", csv_file_path)
        data.to_csv(str(csv_file_path), index=False)

    def _get_csvw_table_schema(self) -> dict:
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
                "valueUrl": self._new_uri_helper.get_concept_uri("{+parent_notation}"),
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
        ]

        if isinstance(self.new_code_list, CompositeQbCodeList):
            _logger.debug("Code list is composite. Linking to original concept URIs.")

            csvw_columns.append(
                {
                    "titles": "Original Concept URI",
                    "name": "uri",
                    "required": True,
                    "propertyUrl": "owl:sameAs",
                    "valueUrl": "{+uri}",
                }
            )

        csvw_columns.append(
            {
                "virtual": True,
                "name": "virt_inScheme",
                "required": True,
                "propertyUrl": "skos:inScheme",
                "valueUrl": self._new_uri_helper.get_scheme_uri(),
            }
        )

        csvw_columns.append(
            {
                "virtual": True,
                "name": "virt_type",
                "required": True,
                "propertyUrl": "rdf:type",
                "valueUrl": "skos:Concept",
            }
        )
        return {
            "columns": csvw_columns,
            "aboutUrl": self._new_uri_helper.get_concept_uri("{+notation}"),
            "primaryKey": CODE_LIST_NOTATION_COLUMN_NAME,
        }

    def _get_csvw_metadata(self) -> dict:
        scheme_uri = self._new_uri_helper.get_scheme_uri()
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
        if isinstance(self.new_code_list, CompositeQbCodeList):
            for variant_uri in self.new_code_list.variant_of_uris:
                concept_scheme_with_metadata.variant.add(ExistingResource(variant_uri))

        self.new_code_list.metadata.configure_dcat_dataset(concept_scheme_with_metadata)
        self.new_code_list.copy_arbitrary_triple_fragments_to_resources(
            {
                RdfSerialisationHint.CatalogDataset: concept_scheme_with_metadata,
                RdfSerialisationHint.ConceptScheme: concept_scheme_with_metadata,
            }
        )
        return concept_scheme_with_metadata

    def _get_code_list_data(self) -> pd.DataFrame:
        data_frame = pd.DataFrame(
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

        if isinstance(self.new_code_list, CompositeQbCodeList):
            data_frame["Original Concept URI"] = [
                c.existing_concept_uri for c in self.new_code_list.concepts
            ]

        return data_frame
