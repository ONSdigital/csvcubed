"""
Code List Config
----------------

Models for representing code list config.
"""

from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass, field
from pathlib import Path

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.utils.json import load_json_document
from csvcubed.models.cube.qb.components import NewQbConcept
from csvcubed.readers.catalogmetadata.v1.catalog_metadata_reader import (
    metadata_from_dict,
)

CODE_LIST_CONFIG_DEFAULT_URL = "https://purl.org/csv-cubed/code-list-config/v1"


@dataclass
class CodeListConfigSort(DataClassBase):
    """Model for representing the sort object in code list config."""

    by: str
    method: str


@dataclass
class CodeListConfigConcept(DataClassBase):
    """Model for representing a code list concept in code list config."""

    label: str
    notation: str
    description: Optional[str] = field(default=None)
    sort_order: Optional[int] = field(default=None)
    same_as: Optional[str] = field(default=None)
    children: List["CodeListConfigConcept"] = field(default_factory=list)


@dataclass
class CodeListConfig(DataClassBase):
    """Model for representing a code list config."""

    sort: Optional[CodeListConfigSort] = field(default=None)
    concepts: List[CodeListConfigConcept] = field(default_factory=list)
    schema: str = field(default=CODE_LIST_CONFIG_DEFAULT_URL)
    # Using CatalogMetadata in the dataclass requires providing default_factory as otherwise, the metadata itself needs to be provided. Since we want have the metadata at initialisation, the default_factory below is defined.
    metadata: CatalogMetadata = field(
        default_factory=lambda: CatalogMetadata("Metadata")
    )

    def _apply_sort_to_concepts(
        self, concepts: List[CodeListConfigConcept]
    ) -> List[CodeListConfigConcept]:
        if self.sort.by != "label" and self.sort.by != "notation":
            raise Exception(
                f"Unsupported sort by {self.sort.by}. The supported options are 'label' and 'notation'."
            )
        if self.sort.method != "ascending" and self.sort.by != "descending":
            raise Exception(
                f"Unsupported sort method {self.sort.method}. The supported options are 'ascending' and 'descending'."
            )

        # First sorting by the sort object defined in the schema.
        sorted_concepts = sorted(
            concepts,
            key=lambda x: x.label if self.sort.by == "label" else "notation",
            reverse=True if self.sort.method == "descending" else False,
        )

        # Then updating the sort order by prioritising the sort_order set per concept.
        for idx, concept in enumerate(sorted_concepts):
            if concept.sort_order:
                if concept.sort_order > len(concepts) - 1:
                    raise Exception(
                        f"Invalid sort order for the concept with notation {concept.notation}."
                    )
                print("hereffff")
                sorted_concepts.remove(concept)
                sorted_concepts.insert(concept.sort_order, concept)
            else:
                concept.sort_order = idx

        print("sorted_concepts: ", sorted_concepts)
        return sorted_concepts

    def _get_parent_of_concept(
        self,
        concepts: List[CodeListConfigConcept],
        target_concept: CodeListConfigConcept,
    ) -> Optional[CodeListConfigConcept]:
        """
        Finds the parent concept of the given concept, if exists.
        """
        for parent_concept in concepts:
            for child_concept in parent_concept.children:
                if child_concept.notation == target_concept.notation:
                    return parent_concept
                elif any(child_concept.children):
                    return self._get_parent_of_concept([child_concept], target_concept)
        return None

    @classmethod
    def from_json_file(cls, file_path: Path) -> Tuple["CodeListConfig", Dict]:
        """
        Converts code list config json to `CodeListConfig`.
        """
        code_list_dict = load_json_document(file_path)
        schema = code_list_dict.get("$schema", CODE_LIST_CONFIG_DEFAULT_URL)

        code_list_config = cls.from_dict(code_list_dict)
        code_list_config.schema = schema
        code_list_config.metadata = metadata_from_dict(code_list_dict)

        return (code_list_config, code_list_dict)

    def apply_sort(
        self,
        parent_concept: Optional[CodeListConfigConcept],
    ):
        if parent_concept is None:
            self.concepts = self._apply_sort_to_concepts(self.concepts)
            print(self.concepts)
        else:
            parent_concept.children = self._apply_sort_to_concepts(
                parent_concept.children
            )
            for child_concept in parent_concept.children:
                if any(child_concept.children):
                    self.apply_sort(child_concept)

    @property
    def new_qb_concepts(self) -> list[NewQbConcept]:
        """
        Converts concepts of type CodeListConfigConcept to concepts of type NewQbConcept whilst maintaining the hierarchy.
        """

        new_qb_concepts: list[NewQbConcept] = []
        if self.concepts:
            concepts: list[CodeListConfigConcept] = list(self.concepts)
            for concept in concepts:
                parent_concept = self._get_parent_of_concept(self.concepts, concept)
                new_qb_concepts.append(
                    NewQbConcept(
                        label=concept.label,
                        code=concept.notation,
                        parent_code=parent_concept.notation if parent_concept else None,
                        sort_order=concept.sort_order,
                        description=concept.description,
                    )
                )
                if any(concept.children):
                    concepts += concept.children
        print(new_qb_concepts)

        return new_qb_concepts
