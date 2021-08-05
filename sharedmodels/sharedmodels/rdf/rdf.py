"""
RDF Properties
--------------
"""
from typing import Annotated, Optional
from rdflib import RDFS, RDF


from .resource import NewResource, PropertyStatus, MaybeResource, map_str_to_en_literal, map_resource_to_uri
from .triple import Triple


class Property(NewResource):
    subPropertyOf: Annotated[MaybeResource["Property"], Triple(RDFS.subPropertyOf, PropertyStatus.optional,
                                                               map_resource_to_uri)]

    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(RDF.Property)


class PropertyWithLabel(Property):
    label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]


class PropertyWithMetadata(PropertyWithLabel):
    comment: Annotated[Optional[str], Triple(RDFS.comment, PropertyStatus.recommended, map_str_to_en_literal)]
