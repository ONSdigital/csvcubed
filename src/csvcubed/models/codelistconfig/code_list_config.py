"""
Code List Config
----------------

Models for representing code list config.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from csvcubedmodels.dataclassbase import DataClassBase

from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components import NewQbConcept
from csvcubed.models.cube.qb.components.concept import DuplicatedQbConcept
from csvcubed.readers.catalogmetadata.v1.catalog_metadata_reader import (
    metadata_from_dict,
)
from csvcubed.utils.json import load_json_document

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
    uri_safe_identifier_override: Optional[str] = field(default=None)


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

    def __post_init__(self):
        # Sorting top-level concepts.
        self.concepts = self._sort_concepts(self.concepts)
        self._apply_sort_to_child_concepts(self.concepts)

    def _apply_sort_to_child_concepts(self, concepts: List[CodeListConfigConcept]):
        """
        Sorting children in each parent concept seperately.
        """
        for concept in concepts:
            if any(concept.children):
                concept.children = self._sort_concepts(concept.children)
                self._apply_sort_to_child_concepts(concept.children)

    def _assign_sort_order_to_concepts(
        self,
        concepts_without_sort_order: List[CodeListConfigConcept],
        user_defined_sort_orders: Set[int],
    ) -> List[CodeListConfigConcept]:
        """Assinging a sort order to concepts without sort order whilst avoiding conflicts with the sort orders already used by the user."""

        sort_order: int = 0
        concepts: List[CodeListConfigConcept] = []
        for concept in concepts_without_sort_order:
            while sort_order in user_defined_sort_orders:
                sort_order += 1
            concept.sort_order = sort_order
            concepts.append(concept)
            sort_order += 1

        return concepts

    def _sort_concepts(
        self, concepts: List[CodeListConfigConcept]
    ) -> List[CodeListConfigConcept]:
        """
        Sorting concepts based on the sort object and sort order defined in the code list json.
        """
        # Step 1: Identify sort orders defined by the user in code list config json.
        user_defined_sort_orders: Set[int] = {
            concept.sort_order for concept in concepts if concept.sort_order is not None
        }

        # Step 2: Identify the concepts with and without sort order.
        concepts_with_sort_order: List[CodeListConfigConcept] = [
            concept for concept in concepts if concept.sort_order is not None
        ]
        concepts_without_sort_order: List[CodeListConfigConcept] = [
            concept for concept in concepts if concept.sort_order is None
        ]

        # Step 3: If the sort object is defined, concepts without a sort order will be sorted by the sort object first.
        if self.sort is not None:
            if self.sort.by != "label" and self.sort.by != "notation":
                raise Exception(
                    f"Unsupported sort by {self.sort.by}. The supported options are 'label' and 'notation'."
                )
            if self.sort.method != "ascending" and self.sort.by != "descending":
                raise Exception(
                    f"Unsupported sort method {self.sort.method}. The supported options are 'ascending' and 'descending'."
                )

            concepts_without_sort_order.sort(
                key=lambda concept: (
                    concept.label
                    if self.sort and self.sort.by == "label"
                    else concept.notation,
                ),
                reverse=True if self.sort.method == "descending" else False,
            )

        # Step 4: Fianlly, all the concepts are sorted by the sort order.
        all_concepts = concepts_with_sort_order + self._assign_sort_order_to_concepts(
            concepts_without_sort_order, user_defined_sort_orders
        )

        sorted_concepts: List[CodeListConfigConcept] = sorted(
            all_concepts,
            key=lambda concept: concept.sort_order is not None and concept.sort_order,
            reverse=False,
        )

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
                parent_code = (
                    maybe_parent_concept.notation if maybe_parent_concept else None
                )
                if concept.same_as:
                    new_qb_concepts.append(
                        DuplicatedQbConcept(
                            label=concept.label,
                            code=concept.notation,
                            parent_code=parent_code,
                            sort_order=concept.sort_order,
                            description=concept.description,
                            uri_safe_identifier_override=concept.uri_safe_identifier_override,
                            existing_concept_uri=concept.same_as,
                        )
                    )
                else:
                    new_qb_concepts.append(
                        NewQbConcept(
                            label=concept.label,
                            code=concept.notation,
                            parent_code=parent_code,
                            sort_order=concept.sort_order,
                            description=concept.description,
                            uri_safe_identifier_override=concept.uri_safe_identifier_override,
                        )
                    )
                if any(concept.children):
                    concepts_with_maybe_parent += [
                        (child, concept) for child in concept.children
                    ]

        return new_qb_concepts
