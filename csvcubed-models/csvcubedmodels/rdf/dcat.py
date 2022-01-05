"""
DCAT
----
"""
from rdflib import Literal, URIRef
from typing import Annotated as Ann, Set, Optional
from datetime import datetime


from .triple import Triple, PropertyStatus
from .resource import (
    NewMetadataResource,
    map_str_to_en_literal,
    map_resource_to_uri,
    Resource as RdfResource,
)
from csvcubedmodels.rdf.namespaces import DCAT, DCTERMS, XSD, PROV, ODRL2, FOAF


class Resource(NewMetadataResource):

    access_rights: Ann[
        str, Triple(DCTERMS.accessRights, PropertyStatus.recommended, URIRef)
    ]
    contact_point: Ann[
        Optional[str], Triple(DCAT.contactPoint, PropertyStatus.recommended, URIRef)
    ]  # Todo: VCARD
    creator: Ann[
        Optional[str], Triple(DCTERMS.creator, PropertyStatus.recommended, URIRef)
    ]
    description: Ann[
        Optional[str],
        Triple(DCTERMS.description, PropertyStatus.recommended, map_str_to_en_literal),
    ]
    title: Ann[
        str, Triple(DCTERMS.title, PropertyStatus.recommended, map_str_to_en_literal)
    ]
    issued: Ann[
        datetime, Triple(DCTERMS.issued, PropertyStatus.recommended, Literal)
    ]  # date/time
    modified: Ann[
        datetime, Triple(DCTERMS.modified, PropertyStatus.recommended, Literal)
    ]
    language: Ann[str, Triple(DCTERMS.language, PropertyStatus.recommended, Literal)]
    publisher: Ann[
        Optional[str], Triple(DCTERMS.publisher, PropertyStatus.recommended, URIRef)
    ]
    identifier: Ann[
        str, Triple(DCTERMS.identifier, PropertyStatus.recommended, Literal)
    ]
    themes: Ann[
        Set[str], Triple(DCAT.theme, PropertyStatus.recommended, URIRef)
    ]  # skos:Concept
    type: Ann[
        str, Triple(DCTERMS.type, PropertyStatus.recommended, URIRef)
    ]  # skos:Concept
    relation: Ann[str, Triple(DCTERMS.relation, PropertyStatus.recommended, URIRef)]
    qualified_relation: Ann[
        str, Triple(DCAT.qualifiedRelation, PropertyStatus.recommended, URIRef)
    ]
    keywords: Ann[
        Set[str],
        Triple(DCAT.keyword, PropertyStatus.recommended, map_str_to_en_literal),
    ]
    landing_page: Ann[
        Set[str], Triple(DCAT.landingPage, PropertyStatus.recommended, URIRef)
    ]
    qualified_attribution: Ann[
        str, Triple(PROV.qualifiedAttribution, PropertyStatus.recommended, URIRef)
    ]
    license: Ann[
        Optional[str], Triple(DCTERMS.license, PropertyStatus.recommended, URIRef)
    ]
    rights: Ann[
        Optional[str], Triple(DCTERMS.rights, PropertyStatus.recommended, URIRef)
    ]
    has_policy: Ann[
        Optional[str], Triple(ODRL2.hasPolicy, PropertyStatus.recommended, URIRef)
    ]
    is_referenced_by: Ann[
        Optional[str],
        Triple(DCTERMS.isReferencedBy, PropertyStatus.recommended, URIRef),
    ]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)
        self.rdf_types.add(DCAT.Resource)
        self.themes = set()
        self.keywords = set()
        self.landing_page = set()


class Dataset(Resource):

    accrual_periodicity: Ann[
        str, Triple(DCTERMS.accrualPeriodicity, PropertyStatus.recommended, URIRef)
    ]
    spatial: Ann[str, Triple(DCTERMS.spatial, PropertyStatus.recommended, URIRef)]
    spatial_resolution_in_meters: Ann[
        float,
        Triple(
            DCAT.spatialResolutionInMeters,
            PropertyStatus.optional,
            lambda l: Literal(l, XSD.decimal),
        ),
    ]
    temporal: Ann[str, Triple(DCTERMS.temporal, PropertyStatus.recommended, URIRef)]
    temporal_resolution: Ann[
        str,
        Triple(
            DCAT.temporalResolution,
            PropertyStatus.optional,
            lambda l: Literal(l, XSD.duration),
        ),
    ]
    """https://github.com/RDFLib/rdflib/pull/808"""
    was_generated_by: Ann[
        str, Triple(PROV.wasGeneratedBy, PropertyStatus.optional, URIRef)
    ]

    def __init__(self, uri: str):
        Resource.__init__(self, uri)
        self.rdf_types.add(DCAT.Dataset)


class CatalogRecord(NewMetadataResource):

    title: Ann[
        str, Triple(DCTERMS.title, PropertyStatus.mandatory, map_str_to_en_literal)
    ]
    description: Ann[
        Optional[str],
        Triple(DCTERMS.description, PropertyStatus.recommended, map_str_to_en_literal),
    ]
    issued: Ann[datetime, Triple(DCTERMS.issued, PropertyStatus.mandatory, Literal)]
    modified: Ann[
        datetime, Triple(DCTERMS.modified, PropertyStatus.recommended, Literal)
    ]
    primary_topic: Ann[
        RdfResource[Resource],
        Triple(FOAF.primaryTopic, PropertyStatus.mandatory, map_resource_to_uri),
    ]
    conforms_to: Ann[
        str, Triple(DCTERMS.conformsTo, PropertyStatus.recommended, URIRef)
    ]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)
        self.rdf_types.add(DCAT.CatalogRecord)


class Catalog(Dataset):
    homepage: Ann[str, Triple(FOAF.homepage, PropertyStatus.recommended, URIRef)]
    theme_taxonomy: Ann[
        str, Triple(DCAT.themeTaxonomy, PropertyStatus.optional, URIRef)
    ]
    has_part: Ann[str, Triple(DCTERMS.hasPart, PropertyStatus.optional, URIRef)]
    dataset: Ann[str, Triple(DCAT.dataset, PropertyStatus.recommended, URIRef)]
    service: Ann[str, Triple(DCAT.service, PropertyStatus.recommended, URIRef)]
    catalog: Ann[str, Triple(DCAT.catalog, PropertyStatus.optional, URIRef)]
    records: Ann[
        Set[RdfResource[CatalogRecord]],
        Triple(DCAT.record, PropertyStatus.recommended, map_resource_to_uri),
    ]

    def __init__(self, uri: str):
        Dataset.__init__(self, uri)
        self.rdf_types.add(DCAT.Catalog)

        self.records = set()
