"""
Catalog Metadata (DCAT)
-----------------------
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union
from csvcubedmodels.rdf import dcat
from pathlib import Path

from csvcubed.models.cube.catalog import CatalogMetadataBase
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.utils.validators.uri import validate_uri, validate_uris_in_list


@dataclass
class CatalogMetadata(CatalogMetadataBase, UriIdentifiable):
    identifier: Optional[str] = None
    summary: Optional[str] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    creator_uri: Optional[str] = field(default=None, repr=False)
    publisher_uri: Optional[str] = field(default=None, repr=False)
    landing_page_uris: list[str] = field(default_factory=list, repr=False)
    theme_uris: list[str] = field(default_factory=list, repr=False)
    keywords: list[str] = field(default_factory=list, repr=False)
    dataset_issued: Optional[datetime] = field(default=None, repr=False)
    dataset_modified: Optional[datetime] = field(default=None, repr=False)
    license_uri: Optional[str] = field(default=None, repr=False)
    public_contact_point_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    # spatial_bound_uri: Optional[str] = field(default=None, repr=False)
    # temporal_bound_uri: Optional[str] = field(default=None, repr=False)

    _creator_uri_validator = validate_uri("creator_uri", is_optional=True)
    _publisher_uri_validator = validate_uri("publisher_uri", is_optional=True)
    _landing_page_uris_validator = validate_uris_in_list(
        "landing_page_uris", is_optional=True
    )
    _license_uri_validator = validate_uri("license_uri", is_optional=True)
    # _spatial_bound_uri_validator = validate_uri("spatial_bound_uri", is_optional=True)
    # _temporal_bound_uri_validator = validate_uri("temporal_bound_uri", is_optional=True)
    _public_contact_point_uri_validator = validate_uri(
        "public_contact_point_uri", is_optional=True
    )

    def to_json_file(self, file_path: Path) -> None:
        with open(file_path, "w+") as f:
            json.dump(self.as_json_dict(), f, indent=4)

    @classmethod
    def from_json_file(cls, file_path: Path) -> "CatalogMetadata":
        with open(file_path, "r") as f:
            dict_structure = json.load(f)

        return cls.from_dict(dict_structure)

    def get_issued(self) -> Optional[datetime]:
        return self.dataset_issued

    def get_description(self) -> Optional[str]:
        return self.description

    def get_identifier(self) -> str:
        return self.identifier or self.title

    def configure_dcat_dataset(self, dataset: dcat.Dataset) -> None:
        dt_now = datetime.now()
        dt_issued = self.dataset_issued or dt_now

        dataset.label = dataset.title = self.title
        dataset.issued = dt_issued
        dataset.modified = self.dataset_modified or dt_issued
        dataset.comment = self.summary
        dataset.description = self.description
        dataset.license = self.license_uri
        dataset.creator = self.creator_uri
        dataset.publisher = self.publisher_uri
        dataset.landing_page = set(self.landing_page_uris)
        dataset.themes = set(self.theme_uris)
        dataset.keywords = set(self.keywords)
        dataset.contact_point = self.public_contact_point_uri
        dataset.identifier = self.get_identifier()
