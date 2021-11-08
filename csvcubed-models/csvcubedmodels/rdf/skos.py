"""
SKOS
----
"""
from typing import Annotated, Set, Union

from rdflib import URIRef

from csvcubedmodels.rdf.resource import (
    NewResource,
    NewResourceWithLabel,
    MaybeResource,
    Resource,
    map_resource_to_uri,
)
from csvcubedmodels.rdf.triple import Triple, PropertyStatus

CollectionMemberType = Union["Concept", "Collection"]


class Collection(NewResource):
    """Collection -"""

    members: Annotated[
        Set[Resource[CollectionMemberType]],
        Triple(
            URIRef("http://www.w3.org/2004/02/skos/core#member"),
            PropertyStatus.recommended,
            map_resource_to_uri,
        ),
    ]
    """has member - """

    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(URIRef("http://www.w3.org/2004/02/skos/core#Collection"))
        self.members = set()


class OrderedCollection(Collection):
    """Ordered Collection -"""

    memberList: Annotated[
        list,
        Triple(
            URIRef("http://www.w3.org/2004/02/skos/core#memberList"),
            PropertyStatus.recommended,
            map_resource_to_uri,
        ),
    ]
    """has member list - For any resource, every item in the list given as the value of the
      skos:memberList property is also a value of the skos:member property."""

    def __init__(self, uri: str):
        Collection.__init__(self, uri)
        self.rdf_types.add(
            URIRef("http://www.w3.org/2004/02/skos/core#OrderedCollection")
        )
        self.memberList = []


class ConceptScheme(NewResourceWithLabel):
    """Concept Scheme -"""

    hasTopConcepts: Annotated[
        Set["Concept"],
        Triple(
            URIRef("http://www.w3.org/2004/02/skos/core#hasTopConcept"),
            PropertyStatus.recommended,
            map_resource_to_uri,
        ),
    ]
    """has top concept - """

    variant: Annotated[
        Set[Resource["ConceptScheme"]],
        Triple(
            URIRef("http://rdf-vocabulary.ddialliance.org/xkos#variant"),
            PropertyStatus.optional,
            map_resource_to_uri,
        ),
    ]
    """xkos:variant - `ConceptScheme` s from which this scheme derives."""

    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(URIRef("http://www.w3.org/2004/02/skos/core#ConceptScheme"))
        self.hasTopConcepts = set()
        self.variant = set()


class Concept(NewResourceWithLabel):
    """Concept -"""

    topConceptOf: Annotated[
        "ConceptScheme",
        Triple(
            URIRef("http://www.w3.org/2004/02/skos/core#topConceptOf"),
            PropertyStatus.recommended,
            map_resource_to_uri,
        ),
    ]
    """is top concept in scheme - """

    semanticRelation: Annotated[
        MaybeResource["Concept"],
        Triple(
            URIRef("http://www.w3.org/2004/02/skos/core#semanticRelation"),
            PropertyStatus.recommended,
            map_resource_to_uri,
        ),
    ]
    """is in semantic relation with - """

    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(URIRef("http://www.w3.org/2004/02/skos/core#Concept"))
