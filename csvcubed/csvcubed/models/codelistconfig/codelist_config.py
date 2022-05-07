import json
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.utils.json import load_json_document
from csvcubed.models.cube.qb.components import NewQbConcept


@dataclass
class CodeListConfigSort:
    """Add Description"""

    by: str
    method: str


@dataclass
class CodeListConfigConcept:
    """Add Description"""

    label: str
    notation: str
    parent_notation: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    sort_order: Optional[int] = field(default=None)
    same_as: Optional[str] = field(default=None)
    children: Optional[list["CodeListConfigConcept"]] = field(default=None)

    @classmethod
    def from_dict(cls, concept_dict: dict) -> "CodeListConfigConcept":
        """
        Add Description

        Member of :class:``.

        :return: ``
        """
        if "children" in concept_dict:
            for child_concepts_dict in concept_dict.pop("children"):
                child_concepts_dict["parent_notation"] = concept_dict["notation"]
                CodeListConfigConcept.from_dict(child_concepts_dict)

        return CodeListConfigConcept(**concept_dict)


@dataclass
class CodeListConfig:
    """Add Description"""

    schema: str
    metadata: CatalogMetadata
    sort: Optional[CodeListConfigSort] = field(default=None)
    concepts: Optional[list[CodeListConfigConcept]] = field(default=None)

    @classmethod
    def from_json_file(cls, file_path: Path) -> "CodeListConfig":
        """
        Add Description

        Member of :class:``.

        :return: `CodeListConfig`.
        """
        code_list_dict = load_json_document(file_path)
        schema = code_list_dict.pop("$schema")
        sort = code_list_dict.pop("sort")
        concepts = [
            CodeListConfigConcept.from_dict(concept_dict)
            for concept_dict in code_list_dict.pop("concepts")
        ]
        metadata = CatalogMetadata(**code_list_dict)

        return CodeListConfig(schema, metadata, sort, concepts)

    @property
    def new_qb_concepts(self) -> list[NewQbConcept]:
        """
        Add Description
        """
        new_qb_concepts: list[NewQbConcept] = []
        if self.concepts:
            for concept in self.concepts:
                new_qb_concepts.append(
                    NewQbConcept(
                        label=concept.label,
                        code=concept.notation,
                        parent_code=concept.parent_notation,
                        sort_order=concept.sort_order,
                        description=concept.description,
                        same_as=concept.same_as,
                    )
                )

        return new_qb_concepts
