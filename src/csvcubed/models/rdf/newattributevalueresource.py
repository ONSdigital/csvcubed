"""
New Attribute Value
-------------------
"""
from typing import Annotated, Optional

from csvcubedmodels.rdf import (
    ExistingResource,
    MaybeResource,
    NewMetadataResource,
    PropertyStatus,
    Triple,
    map_resource_to_uri,
)
from csvcubedmodels.rdf.namespaces import RDFS, SKOS


class NewAttributeValueResource(NewMetadataResource):
    """
    New RDF Resource representing a value that an attribute can take.
    """

    source_uri: Annotated[
        Optional[ExistingResource],
        Triple(RDFS.isDefinedBy, PropertyStatus.recommended, map_resource_to_uri),
    ]

    parent_attribute_value_uri: Annotated[
        MaybeResource["NewAttributeValueResource"],
        Triple(SKOS.broader, PropertyStatus.recommended, map_resource_to_uri),
    ]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)
