"""
Catalog Metadata (DCAT)
-----------------------
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from sharedmodels.rdf import dcat

from csvqb.models.cube.catalog import CatalogMetadataBase
from csvqb.models.uriidentifiable import UriIdentifiable


@dataclass
class CatalogMetadata(CatalogMetadataBase, UriIdentifiable):
    theme_uris: list[str] = field(default_factory=list, repr=False)
    keywords: list[str] = field(default_factory=list, repr=False)
    issued: datetime = field(default_factory=lambda: datetime.now(), repr=False)
    summary: Optional[str] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    creator_uri: Optional[str] = field(default=None, repr=False)
    publisher_uri: Optional[str] = field(default=None, repr=False)
    landing_page_uri: Optional[str] = field(default=None, repr=False)
    license_uri: Optional[str] = field(default=None, repr=False)
    public_contact_point_uri: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def __post_init__(self):
        print("Hello.")

    def get_issued(self) -> datetime:
        return self.issued

    def get_description(self) -> Optional[str]:
        return self.description

    def get_identifier(self) -> str:
        return self.title

    def configure_dcat_dataset(self, dataset: dcat.Dataset) -> None:
        dt_now = datetime.now()
        dataset.label = dataset.title = self.title
        dataset.issued = self.issued or dt_now
        dataset.modified = dt_now
        dataset.comment = self.summary
        dataset.description = self.description
        dataset.license = self.license_uri
        dataset.creator = self.creator_uri
        dataset.publisher = self.publisher_uri
        dataset.landing_page = self.landing_page_uri
        dataset.themes = set(self.theme_uris)
        dataset.keywords = set(self.keywords)
        dataset.contact_point = self.public_contact_point_uri
