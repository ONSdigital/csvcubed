"""
CodeList Writer
---------------

Write `NewQbCodeList`s to CSV-Ws as `skos:ConceptScheme` s with DCAT2 metadata.
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas as pd
from csvcubedmodels.rdf import ExistingResource

from csvcubed.models.cube.qb.components import (
    CompositeQbCodeList,
    DuplicatedQbConcept,
    NewQbCodeList,
    RdfSerialisationHint,
)
from csvcubed.models.cube.qb.components.concept import NewQbConcept
from csvcubed.models.cube.uristyle import URIStyle
from csvcubed.models.rdf import prov
from csvcubed.models.rdf.conceptschemeincatalog import ConceptSchemeInCatalog
from csvcubed.utils.dict import rdf_resource_to_json_ld
from csvcubed.utils.version import get_csvcubed_version_uri
from csvcubed.writers.helpers.skoscodelistwriter.newresourceurigenerator import (
    NewResourceUriGenerator,
)
from csvcubed.writers.writerbase import WriterBase

_logger = logging.getLogger(__name__)


@dataclass
class SkosCodeListWriter(WriterBase):
    new_code_list: NewQbCodeList
    default_uri_style: URIStyle = URIStyle.Standard
    csv_file_name: str = field(init=False)
    uri_helper: NewResourceUriGenerator = field(init=False)

    @property
    def csv_metadata_file_name(self) -> str:
        return f"{self.csv_file_name}-metadata.json"

    @staticmethod
    def has_duplicated_qb_concepts(code_list: NewQbCodeList) -> bool:
        return any(
            True
            for concept in code_list.concepts
            if isinstance(concept, DuplicatedQbConcept)
        )

    def __post_init__(self):
        self.csv_file_name = f"{self.new_code_list.metadata.uri_safe_identifier}.csv"
        _logger.debug(
            "Initialising %s with CSV output set to '%s'",
            SkosCodeListWriter.__name__,
            self.csv_file_name,
        )
        self.uri_helper = NewResourceUriGenerator(
            self.new_code_list, default_uri_style=self.default_uri_style
        )

    def write(self, output_directory: Path) -> None:
        csv_file_path = (output_directory / self.csv_file_name).absolute()
        metadata_file_path = (output_directory / self.csv_metadata_file_name).absolute()
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
                "titles": "Uri Identifier",
                "name": "uri_identifier",
                "required": True,
                "suppressOutput": True,
            },
            {
                "titles": "Label",
                "name": "label",
                "required": True,
                "propertyUrl": "rdfs:label",
            },
            {
                "titles": "Notation",
                "name": "notation",
                "required": True,
                "propertyUrl": "skos:notation",
            },
            {
                "titles": "Parent Uri Identifier",
                "name": "parent_uri_identifier",
                "required": False,
                "propertyUrl": "skos:broader",
                "valueUrl": self.uri_helper.get_concept_uri("{+parent_uri_identifier}"),
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

        if isinstance(
            self.new_code_list, CompositeQbCodeList
        ) or self.has_duplicated_qb_concepts(self.new_code_list):
            _logger.debug(
                "Code list is composite has a duplicated concept. Linking to original concept URIs."
            )

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
                "valueUrl": self.uri_helper.get_scheme_uri(),
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
            "aboutUrl": self.uri_helper.get_concept_uri("{+uri_identifier}"),
            "primaryKey": "uri_identifier",
        }

    def _get_csvw_metadata(self) -> dict:
        scheme_uri = self.uri_helper.get_scheme_uri()
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

        generation_activity = prov.Activity(self.uri_helper.get_activity_uri())
        generation_activity.used = ExistingResource(get_csvcubed_version_uri())
        concept_scheme_with_metadata.was_generated_by = generation_activity

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

    def _get_parent_concept(self, parent_code: str) -> NewQbConcept:
        filtered_concepts: List[NewQbConcept] = [
            c for c in self.new_code_list.concepts if c.code == parent_code
        ]
        if len(filtered_concepts) == 0:
            raise Exception(
                f"Unable to find parent concept with parent code {parent_code}"
            )
        elif len(filtered_concepts) > 1:
            raise Exception(
                f"More than one concept found for parent code {parent_code}"
            )

        return filtered_concepts[0]

    def _get_code_list_data(self) -> pd.DataFrame:
        data_frame = pd.DataFrame(
            {
                "Uri Identifier": [
                    c.uri_safe_identifier for c in self.new_code_list.concepts
                ],
                "Label": [c.label for c in self.new_code_list.concepts],
                "Notation": [c.code for c in self.new_code_list.concepts],
                "Parent Uri Identifier": [
                    self._get_parent_concept(c.parent_code).uri_safe_identifier
                    if c.parent_code
                    else None
                    for c in self.new_code_list.concepts
                ],
                "Sort Priority": [
                    i if c.sort_order is None else c.sort_order
                    for i, c in enumerate(self.new_code_list.concepts)
                ],
                "Description": [c.description for c in self.new_code_list.concepts],
            }
        )

        if isinstance(
            self.new_code_list, CompositeQbCodeList
        ) or self.has_duplicated_qb_concepts(self.new_code_list):
            data_frame["Original Concept URI"] = [
                c.existing_concept_uri if isinstance(c, DuplicatedQbConcept) else None
                for c in self.new_code_list.concepts
            ]

        return data_frame
