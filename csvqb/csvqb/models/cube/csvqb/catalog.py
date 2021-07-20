from datetime import datetime
from typing import Optional, List

from csvqb.models.validationerror import ValidationError
from csvqb.utils.uri import uri_safe
from csvqb.models.cube.catalog import CatalogMetadataBase


class CatalogMetadata(CatalogMetadataBase):

    def __init__(self,
                 title: str,
                 uri_safe_identifier: Optional[str] = None,
                 summary: Optional[str] = None,
                 description: Optional[str] = None,
                 creator_uri: Optional[str] = None,
                 publisher_uri: Optional[str] = None,
                 issued: Optional[datetime] = None,
                 theme_uris: List[str] = [],
                 keywords: List[str] = [],
                 landing_page_uri: Optional[str] = None,
                 license_uri: Optional[str] = None,
                 public_contact_point_uri: Optional[str] = None):
        CatalogMetadataBase.__init__(self, title, description=description, issued=issued)
        self.uri_safe_identifier: str = uri_safe_identifier or uri_safe(title)
        self.summary: Optional[str] = summary
        self.creator_uri: Optional[str] = creator_uri
        self.publisher_uri: Optional[str] = publisher_uri
        self.theme_uris: List[str] = theme_uris
        self.keywords: List[str] = keywords
        self.landing_page_uri: Optional[str] = landing_page_uri
        self.license_uri: Optional[str] = license_uri
        self.public_contact_point_uri: Optional[str] = public_contact_point_uri

    def validate(self) -> List[ValidationError]:
        return CatalogMetadataBase.validate(self) \
               + []  # TODO: augment this
