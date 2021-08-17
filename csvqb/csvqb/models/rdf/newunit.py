"""
New Unit
--------
"""
from typing import Annotated, Optional

from rdflib import RDFS
from sharedmodels.rdf.namespaces import QUDT
from sharedmodels.rdf import NewMetadataResource, Triple, PropertyStatus, map_resource_to_uri, ExistingResource, \
    MaybeResource


class NewUnit(NewMetadataResource):
    source_uri: Annotated[Optional[ExistingResource], Triple(RDFS.isDefinedBy, PropertyStatus.recommended, map_resource_to_uri)]

    parent_unit_uri: Annotated[MaybeResource["NewUnit"], Triple(RDFS.subClassOf, PropertyStatus.recommended, map_resource_to_uri)]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)
        self.rdf_types.add(QUDT.Unit)
