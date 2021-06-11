from rdflib import  Literal, URIRef, DCAT, DCTERMS, XSD, PROV, ODRL2
from typing import Annotated as Ann, List

from .rdfpropertymap import RdfPropertyMap, PropertyStatus
from .rdfresource import RdfMetadataResource, map_str_to_en_literal, map_entity_to_uri


class Resource(RdfMetadataResource):

    accessRights: Ann[str, RdfPropertyMap(DCTERMS.accessRights, PropertyStatus.recommended, URIRef)]
    contactPoint: Ann[str, RdfPropertyMap(DCAT.contactPoint, PropertyStatus.recommended, URIRef)]  # Todo: VCARD
    creator: Ann[str, RdfPropertyMap(DCTERMS.creator, PropertyStatus.recommended, URIRef)]
    description: Ann[str, RdfPropertyMap(DCTERMS.description, PropertyStatus.recommended, map_str_to_en_literal)]
    title: Ann[str, RdfPropertyMap(DCTERMS.title, PropertyStatus.recommended, map_str_to_en_literal)]

    issued: Ann[str, RdfPropertyMap(DCTERMS.issued, PropertyStatus.recommended, Literal)]  # date/time
    """todo: FIX type"""

    modified: Ann[str, RdfPropertyMap(DCTERMS.modified, PropertyStatus.recommended, Literal)]
    """todo: FIX type"""

    language: Ann[str, RdfPropertyMap(DCTERMS.language, PropertyStatus.recommended, Literal)]
    publisher: Ann[str, RdfPropertyMap(DCTERMS.publisher, PropertyStatus.recommended, URIRef)]
    identifier: Ann[str, RdfPropertyMap(DCTERMS.identifier, PropertyStatus.recommended, Literal)]
    theme: Ann[str, RdfPropertyMap(DCAT.theme, PropertyStatus.recommended, URIRef)]  # skos:Concept
    type: Ann[str, RdfPropertyMap(DCTERMS.type, PropertyStatus.recommended, URIRef)]  # skos:Concept
    relation: Ann[str, RdfPropertyMap(DCTERMS.relation, PropertyStatus.recommended, URIRef)]
    qualifiedRelation: Ann[str, RdfPropertyMap(DCAT.qualifiedRelation, PropertyStatus.recommended, URIRef)]
    keyword: Ann[str, RdfPropertyMap(DCAT.keyword, PropertyStatus.recommended, map_str_to_en_literal)]
    landingPage: Ann[str, RdfPropertyMap(DCAT.landingPage, PropertyStatus.recommended, URIRef)]  # foaf:Document
    qualifiedAttribution: Ann[str, RdfPropertyMap(PROV.qualifiedAttribution, PropertyStatus.recommended, URIRef)]
    license: Ann[str, RdfPropertyMap(DCTERMS.license, PropertyStatus.recommended, URIRef)]
    rights: Ann[str, RdfPropertyMap(DCTERMS.rights, PropertyStatus.recommended, URIRef)]
    hasPolicy: Ann[str, RdfPropertyMap(ODRL2.hasPolicy, PropertyStatus.recommended, URIRef)]
    isReferencedBy: Ann[str, RdfPropertyMap(DCTERMS.isReferencedBy, PropertyStatus.recommended, URIRef)]

    def __init__(self, uri: str, rdf_types: List[URIRef]):
        RdfMetadataResource.__init__(self, uri, rdf_types + [DCAT.Resource])


class Dataset(Resource):

    distribution: Ann[str, RdfPropertyMap(DCAT.distribution, PropertyStatus.recommended, map_entity_to_uri)]
    """todo: FIX type"""

    accrualPeriodicity: Ann[str, RdfPropertyMap(DCTERMS.accrualPeriodicity, PropertyStatus.recommended, URIRef)]  # dct:Frequency
    spatial: Ann[str, RdfPropertyMap(DCTERMS.spatial, PropertyStatus.recommended, URIRef)]
    spatialResolutionInMeters: Ann[float, RdfPropertyMap(DCAT.spatialResolutionInMeters, PropertyStatus.optional, lambda l: Literal(l, XSD.decimal))]
    temporal: Ann[str, RdfPropertyMap(DCTERMS.temporal, PropertyStatus.recommended, URIRef)]

    temporalResolution: Ann[str, RdfPropertyMap(DCAT.temporalResolution, PropertyStatus.optional, lambda l: Literal(l, XSD.duration))]
    """todo: FIX type"""

    wasGeneratedBy: Ann[str, RdfPropertyMap(PROV.wasGeneratedBy, PropertyStatus.optional, URIRef)]

    def __init__(self, uri: URIRef):
        Resource.__init__(self, uri, [DCAT.Dataset])
