from typing import Annotated
from rdflib import RDFS, RDF


from .rdfresource import RdfResource, PropertyStatus, map_str_to_en_literal, map_entity_to_uri
from .triple import Triple


class Property(RdfResource):
    subPropertyOf: Annotated["Property", Triple(RDFS.subPropertyOf, PropertyStatus.optional, map_entity_to_uri)]

    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)
        self.rdf_types.add(RDF.Property)


class PropertyWithMetadata(Property):
    label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]
    comment: Annotated[str, Triple(RDFS.comment, PropertyStatus.recommended, map_str_to_en_literal)]

    def __init__(self, uri: str):
        Property.__init__(self, uri)
