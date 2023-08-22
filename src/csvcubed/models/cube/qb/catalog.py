"""
Catalog Metadata (DCAT)
-----------------------
"""
import json
from dataclasses import dataclass, field
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, Optional, Union

from csvcubedmodels.rdf import dcat

from csvcubed.models.cube.catalog import CatalogMetadataBase
from csvcubed.models.uriidentifiable import UriIdentifiable
from csvcubed.models.validatedmodel import ValidationFunction
from csvcubed.utils import validations as v


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
    dataset_issued: Union[datetime, date, None] = field(default=None, repr=False)
    dataset_modified: Union[datetime, date, None] = field(default=None, repr=False)
    license_uri: Optional[str] = field(default=None, repr=False)
    public_contact_point_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)
    # spatial_bound_uri: Optional[str] = field(default=None, repr=False)
    # temporal_bound_uri: Optional[str] = field(default=None, repr=False)

    def _get_validations(self) -> Dict[str, ValidationFunction]:
        return {
            **CatalogMetadataBase._get_validations(self),
            "identifier": v.optional(v.string),
            "summary": v.optional(v.string),
            "description": v.optional(v.string),
            "creator_uri": v.optional(v.uri),
            "publisher_uri": v.optional(v.uri),
            "landing_page_uris": v.list(v.uri),
            "theme_uris": v.list(v.uri),
            "keywords": v.list(v.string),
            "dataset_issued": v.optional(
                v.any_of(v.is_instance_of(date), v.is_instance_of(datetime))
            ),
            "dataset_modified": v.optional(
                v.any_of(v.is_instance_of(date), v.is_instance_of(datetime))
            ),
            "license_uri": v.optional(v.uri),
            "public_contact_point_uri": v.optional(v.uri),
            **UriIdentifiable._get_validations(self),
        }

    def to_json_file(self, file_path: Path) -> None:
        with open(file_path, "w+") as f:
            json.dump(self.as_json_dict(), f, indent=4)

    @classmethod
    def from_json_file(cls, file_path: Path) -> "CatalogMetadata":
        with open(file_path, "r") as f:
            dict_structure = json.load(f)

        return cls.from_dict(dict_structure)

    def get_issued(self) -> Union[datetime, date, None]:
        return self.dataset_issued

    def get_description(self) -> Optional[str]:
        return self.description

    def get_identifier(self) -> str:
        return self.identifier or self.title

    def configure_dcat_distribution(self, distribution: dcat.Distribution) -> None:
        """
        CatalogMetadata properties not currently populated here
        identifier
        creator_uri
        landing_page_uris
        theme_uris
        keywords
        public_contact_point_uri
        uri_safe_identifier_override
        """
        dt_now = datetime.now()
        dt_issued = _convert_date_to_date_time(self.dataset_issued or dt_now)
        distribution.issued = dt_issued
        distribution.modified = _convert_date_to_date_time(
            self.dataset_modified or dt_issued
        )

        distribution.label = distribution.title = self.title
        distribution.description = self.description
        distribution.comment = self.summary
        distribution.publisher = self.publisher_uri
        distribution.license = self.license_uri
        distribution.keywords = self.keywords
        distribution.identifier = self.identifier
        distribution.creator = self.creator_uri
        distribution.landing_page = self.landing_page_uris
        distribution.themes = self.theme_uris
        distribution.keywords = self.keywords

        # 831 TODO
        # Main question - shouldn't Distribution inherit from Resource, not NewMetadataResource?
        # dcat:Distribution properties not yet used
        # distribution.is_distribution_of
        # distribution.access_service
        # distribution.access_url
        # distribution.byte_size
        # distribution.compress_format
        # distribution.download_url
        # distribution.media_type
        # distribution.package_format
        # distribution.spatial
        # distribution.spatial_resolution_in_meters
        # distribution.temporal
        # distribution.temporal_resolution
        # distribution.conforms_to
        # distribution.format
        # distribution.rights
        # distribution.has_policy

        # dcat:Dataset properties (most of these were populated via the dcat:Resource parent class)
        # Direct properties:
        # distribution
        # accrual_periodicity
        # spatial
        # spatial_resolution_in_meters
        # temporal
        # temporal_resolution
        # Inherited from Resource:
        # access_rights
        # contact_point
        # creator
        # description
        # title
        # issued
        # modified
        # language
        # publisher
        # identifier
        # themes
        # type
        # relation
        # qualified_relation
        # keywords
        # landing_page
        # qualified_attribution
        # license
        # rights
        # has_policy
        # is_referenced_by


def _convert_date_to_date_time(dt: Union[datetime, date]) -> datetime:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return datetime.combine(dt, time.min)

    return dt
