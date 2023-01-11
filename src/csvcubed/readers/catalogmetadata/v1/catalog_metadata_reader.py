"""
Catalog Metadata Reader
-----------------------

Functionalities necessary for reading catalog metadata.
"""
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.utils.datetime import parse_iso_8601_date_time
from csvcubed.utils.dict import get_with_func_or_none
from csvcubed.utils.uri import uri_safe


def metadata_from_dict(config: dict) -> CatalogMetadata:
    """
    Converts dict into `CatalogMetadata`.
    """
    themes = config.get("themes", [])
    if themes and isinstance(themes, str):
        themes = [themes]

    keywords = config.get("keywords", [])
    if keywords and isinstance(keywords, str):
        keywords = [keywords]

    return CatalogMetadata(
        identifier=get_with_func_or_none(config, "id", uri_safe),
        title=config["title"],
        description=config.get("description", ""),
        summary=config.get("summary", ""),
        creator_uri=config.get("creator"),
        publisher_uri=config.get("publisher"),
        public_contact_point_uri=config.get("public_contact_point"),
        dataset_issued=get_with_func_or_none(
            config, "dataset_issued", parse_iso_8601_date_time
        ),
        dataset_modified=get_with_func_or_none(
            config, "dataset_modified", parse_iso_8601_date_time
        ),
        license_uri=config.get("license"),
        theme_uris=themes,
        keywords=keywords,
        # spatial_bound_uri=uri_safe(config['spatial_bound'])
        #     if config.get('spatial_bound') else None,
        # temporal_bound_uri=uri_safe(config['temporal_bound'])
        #     if config.get('temporal_bound') else None,
    )
