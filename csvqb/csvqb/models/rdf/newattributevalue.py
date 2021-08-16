"""
New Attribute Value
-------------------
"""
from typing import Annotated, Optional

from rdflib import RDFS
from sharedmodels.rdf import NewMetadataResource, Triple, PropertyStatus, map_resource_to_uri, ExistingResource, \
    MaybeResource


class NewAttributeValue(NewMetadataResource):
    source_uri: Annotated[Optional[ExistingResource], Triple(RDFS.isDefinedBy, PropertyStatus.recommended, map_resource_to_uri)]
    """
    subject predicate object.
    <new_attribute_value> rdfs:isDefinedBy {map_resource_to_uri(source_uri)}. 
    <new_attribute_value> rdfs:isDefinedBy <http://existing-resource-uri>.
    """

    parent_attribute_value_uri: Annotated[MaybeResource["NewAttributeValue"], Triple(RDFS.subClassOf, PropertyStatus.recommended, map_resource_to_uri)]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)
        self.rdf_types.add(RDFS["Class"])

