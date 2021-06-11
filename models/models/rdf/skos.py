from rdflib import SKOS, RDF, RDFS, URIRef, DCTERMS, PROV
from typing import Annotated as Ann

from .rdfresource import RdfMetadataResource, map_str_to_en_literal, map_entity_to_uri
from .rdfpropertymap import RdfPropertyMap, PropertyStatus
from .dcat import Dataset


class ConceptScheme(RdfMetadataResource):
    title: Ann[str, RdfPropertyMap(DCTERMS.title, PropertyStatus.recommended, map_str_to_en_literal)]
    dcat_dataset: Ann[Dataset, RdfPropertyMap(PROV.wasDerivedFrom, PropertyStatus.mandatory, map_entity_to_uri)]

    def __init__(self, uri: URIRef):
        RdfMetadataResource.__init__(self, uri, [SKOS.ConceptScheme])
