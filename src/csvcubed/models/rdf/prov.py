"""
PROV Ontology Models
--------------------

This module holds some models in the prov-o ontology. 
"""
from typing import Annotated

from csvcubedmodels.rdf import NewResource, Resource, Triple, PropertyStatus, map_resource_to_uri, ExistingResource
from csvcubedmodels.rdf.namespaces import PROV

class Activity(NewResource):

    used: Annotated[ExistingResource, Triple(PROV.used, PropertyStatus.optional, map_resource_to_uri)]

    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(PROV.Activity)

class Entity(NewResource):

    was_generated_by: Annotated[Resource[Activity], Triple(PROV.wasGeneratedBy, PropertyStatus.optional, map_resource_to_uri)]

    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(PROV.Entity)