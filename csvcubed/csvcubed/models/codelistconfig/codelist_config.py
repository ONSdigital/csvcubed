import json
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

from csvcubed.models.cube.catalog import CatalogMetadataBase
from csvcubed.utils.json import load_json_document


@dataclass
class CodeListConfigSort:
    """TODO: Add Description"""

    by: str
    method: str


@dataclass
class CodeListConfigConcept:
    """TODO: Add Description"""

    label: str
    description: str
    notation: str
    sort_order: int
    same_as: str


@dataclass
class CodeListConfig:
    """TODO: Add Description"""

    title: str
    description: str
    summary: str
    creator: str
    publisher: str
    dataset_issued: str
    dataset_modified: str
    license: str
    themes: [str]
    keywords: [str]
    sort: CodeListConfigSort
    concepts: [CodeListConfigConcept]

    @classmethod
    def from_json_file(cls, file_path: Path) -> "CodeListConfig":
        code_list_dict = load_json_document(file_path)
        code_list_dict.pop("$schema", None)
        return CodeListConfig(**code_list_dict)
