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
    # Using CatalogMetadata in the dataclass requires providing default_factory as otherwise, the metadata itself needs
    # to be provided. Since we want have the metadata at initialisation, the default_factory below is defined.
    metadata: CatalogMetadata = field(
        default_factory=lambda: CatalogMetadata("Metadata")
    )

    def __post_init__(self):
        if self.sort:
            self._apply_sort(None)
            for parent_concept in self.concepts:
                self._apply_sort(parent_concept)

    def _apply_sort(
        self,
        parent_concept: Optional[CodeListConfigConcept],
    ):
        """
        Sorting the top level concepts and then children in each parent concept seperately.
        """
        if parent_concept is None:
            self.concepts = self._sort_concepts(self.concepts)
        else:
            parent_concept.children = self._sort_concepts(parent_concept.children)
            for child_concept in parent_concept.children:
                if any(child_concept.children):
                    self._apply_sort(child_concept)

    def _sort_concepts(
        self, concepts: List[CodeListConfigConcept]
    ) -> List[CodeListConfigConcept]:
        """
        Sorting concepts based on the sort object and sort order defined in the code list json.
        """
        # If the sort object is not defined, the sorting will default to the sort_order where defined.
        if self.sort is None:
            sorted_concepts: List[CodeListConfigConcept] = sorted(
                concepts,
                key=lambda x: (x.sort_order is None, x.sort_order),
                reverse=False,
            )
            return sorted_concepts

        # Otherwise, the sort object and sort_order both are used for sorting.
        if self.sort.by != "label" and self.sort.by != "notation":
            raise Exception(
                f"Unsupported sort by {self.sort.by}. The supported options are 'label' and 'notation'."
            )
        if self.sort.method != "ascending" and self.sort.by != "descending":
            raise Exception(
                f"Unsupported sort method {self.sort.method}. The supported options are 'ascending' and 'descending'."
            )

        sorted_concepts: List[CodeListConfigConcept] = sorted(
            concepts,
            key=lambda x: (
                x.sort_order is None,
                x.sort_order,
                x.label if self.sort and self.sort.by == "label" else x.notation,
            ),
            reverse=True if self.sort.method == "descending" else False,
        )
        # Assigning the new sort_order to the concepts.
        for idx, concept in enumerate(sorted_concepts):
            concept.sort_order = idx

        return sorted_concepts

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

    @classmethod
    def from_dict(cls, code_list_dict: Dict) -> "CodeListConfig":
        """
        Converts code list config dict to `CodeListConfig`.
        """
        schema = code_list_dict.get("$schema", CODE_LIST_CONFIG_DEFAULT_URL)

        code_list_config = super().from_dict(code_list_dict)
        code_list_config.schema = schema
        code_list_config.metadata = metadata_from_dict(code_list_dict)

        return code_list_config

    @property
    def new_qb_concepts(self) -> list[NewQbConcept]:
        """
        Converts concepts of type CodeListConfigConcept to concepts of type NewQbConcept whilst maintaining the hierarchy.
        """

        new_qb_concepts: list[NewQbConcept] = []
        if self.concepts:
            concepts_with_maybe_parent: list[
                Tuple[CodeListConfigConcept, Optional[CodeListConfigConcept]]
            ] = [(c, None) for c in self.concepts]

            for (concept, maybe_parent_concept) in concepts_with_maybe_parent:
                new_qb_concepts.append(
                    NewQbConcept(
                        label=concept.label,
                        code=concept.notation,
                        parent_code=maybe_parent_concept.notation
                        if maybe_parent_concept
                        else None,
                        sort_order=concept.sort_order,
                        description=concept.description,
                    )
                )
                if any(concept.children):
                    concepts_with_maybe_parent += [
                        (child, concept) for child in concept.children
                    ]

        return new_qb_concepts
