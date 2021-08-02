"""
PMD Config
----------

Holds metadata necessary to configure catalogue metadata in PMD.
"""
from os import getenv


DATASET_CATALOG_URI = "http://gss-data.org.uk/catalog/datasets"
CODE_LIST_CATALOG_URI = "http://gss-data.org.uk/catalog/vocabularies"

SPARQL_ENDPOINT = getenv("SPARQL_URL", default="https://staging.gss-data.org.uk/sparql")
