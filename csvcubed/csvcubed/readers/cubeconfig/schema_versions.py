"""
Schema Versions
---------------

Contains an enum listing the qube-config.json schema versions recognised by csvcubed.
"""
from enum import Enum


class QubeConfigJsonSchemaVersion(Enum):
    DEFAULT_V1_SCHEMA_URL = "https://purl.org/csv-cubed/qube-config/v1.0"
