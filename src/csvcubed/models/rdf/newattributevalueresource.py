"""
New Attribute Value
-------------------
"""
from typing import Annotated, Optional

from csvcubedmodels.rdf.namespaces import RDFS, SKOS
from csvcubedmodels.rdf import (
    NewMetadataResource,
    Triple,
    PropertyStatus,
    map_resource_to_uri,
    ExistingResource,
    MaybeResource,
)


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
