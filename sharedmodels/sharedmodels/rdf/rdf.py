from typing import Annotated, Optional
from rdflib import RDFS, RDF


from .rdfresource import RdfResource, PropertyStatus, MaybeEntity, map_str_to_en_literal, map_resource_to_uri
from .triple import Triple


class Property(RdfResource):
    subPropertyOf: Annotated[MaybeEntity["Property"], Triple(RDFS.subPropertyOf, PropertyStatus.optional,
                                                             map_resource_to_uri)]

    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)
        self.rdf_types.add(RDF.Property)


class PropertyWithMetadata(Property):
    label: Annotated[str, Triple(RDFS.label, PropertyStatus.mandatory, map_str_to_en_literal)]
    comment: Annotated[Optional[str], Triple(RDFS.comment, PropertyStatus.recommended, map_str_to_en_literal)]

    def __init__(self, uri: str):
        Property.__init__(self, uri)
