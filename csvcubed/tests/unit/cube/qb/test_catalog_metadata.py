import datetime

import pytest
from tempfile import TemporaryDirectory
from pathlib import Path

from csvcubed.models.cube.qb.catalog import CatalogMetadata


def test_serialise_and_load_json():
    """
    Ensure that we can correctly serialise and de-serialise all CatalogMetadata fields to JSON.
    """
    with TemporaryDirectory() as tmp_dir_path:
        catalog_metadata = CatalogMetadata(
            title="Some catalog item",
            identifier="some-catalog-thingy",
            uri_safe_identifier_override="some-uri-safe-override",
            description="Some catalog item description",
            summary="Some catalog item summary",
            dataset_issued=datetime.datetime(2010, 1, 1, 1, 1, 1, 1),
            dataset_modified=datetime.datetime(2010, 1, 1, 2, 1, 1, 1),
            theme_uris=["http://some-theme-uri"],
            license_uri="http://some-license-uri",
            keywords=["Some key word"],
            creator_uri="http://some-creator-uri",
            publisher_uri="http://some-publisher-uri",
            public_contact_point_uri="mailto:somecontactpoint@ons.gov.uk",
            landing_page_uris=["http://some-landing-page-uri"],
        )

        tmp_dir_path = Path(tmp_dir_path)
        json_file = tmp_dir_path / "catalog-metadata.json"
        catalog_metadata.to_json_file(json_file)
        reinflated_catalog_metadata = catalog_metadata.from_json_file(json_file)

        assert reinflated_catalog_metadata.title == "Some catalog item"
        assert reinflated_catalog_metadata.identifier == "some-catalog-thingy"
        assert (
            reinflated_catalog_metadata.uri_safe_identifier_override
            == "some-uri-safe-override"
        )
        assert (
            reinflated_catalog_metadata.description == "Some catalog item description"
        )
        assert reinflated_catalog_metadata.summary == "Some catalog item summary"
        assert reinflated_catalog_metadata.dataset_issued == datetime.datetime(
            2010, 1, 1, 1, 1, 1, 1
        )
        assert reinflated_catalog_metadata.dataset_modified == datetime.datetime(
            2010, 1, 1, 2, 1, 1, 1
        )
        assert reinflated_catalog_metadata.theme_uris == ["http://some-theme-uri"]
        assert reinflated_catalog_metadata.license_uri == "http://some-license-uri"
        assert reinflated_catalog_metadata.keywords == ["Some key word"]
        assert reinflated_catalog_metadata.creator_uri == "http://some-creator-uri"
        assert reinflated_catalog_metadata.publisher_uri == "http://some-publisher-uri"
        assert (
            reinflated_catalog_metadata.public_contact_point_uri
            == "mailto:somecontactpoint@ons.gov.uk"
        )
        assert reinflated_catalog_metadata.landing_page_uris == [
            "http://some-landing-page-uri"
        ]


if __name__ == "__main__":
    pytest.main()
