from rdflib import DCAT, VOID, Namespace, URIRef, Literal
from typing import Annotated
from abc import ABC
from datetime import datetime


from models.rdf.triple import Triple, InverseTriple, PropertyStatus
from models.rdf.rdfresource import RdfMetadataResource, map_str_to_markdown, map_entity_to_uri
from models.rdf import dcat
from models.rdf import skos


PMDCAT = Namespace("http://publishmydata.com/pmdcat#")
GDP = Namespace("http://gss-data.org.uk/def/gdp#")


class DatasetContents(RdfMetadataResource, ABC):
    def __init__(self, uri: str):
        RdfMetadataResource.__init__(self, uri)
        self.rdf_types.add(PMDCAT.DatasetContents)


class ConceptScheme(DatasetContents, skos.ConceptScheme):
    def __init__(self, uri: str):
        DatasetContents.__init__(self, uri)
        skos.ConceptScheme.__init__(self, uri)
        self.rdf_types.add(PMDCAT.ConceptScheme)


# todo: Ensure that the DataCube successfully extends a qb:DataSet whenever we get round to representing that in here.
class DataCube(DatasetContents):
    def __init__(self, uri: str):
        DatasetContents.__init__(self, uri)
        self.rdf_types.add(PMDCAT.DataCube)


class Dataset(dcat.Dataset):
    """HoldsCatalog Metadata."""

    metadata_graph: Annotated[str, Triple(PMDCAT.metadataGraph, PropertyStatus.mandatory, URIRef)]
    """Graph where the PMDCAT/DCAT metadata is stored."""

    pmdcat_graph: Annotated[str, Triple(PMDCAT.graph, PropertyStatus.mandatory, URIRef)]
    """Graph where the pmdcat:datasetContents is stored."""

    dataset_contents: Annotated[DatasetContents, Triple(PMDCAT.datasetContents, PropertyStatus.mandatory, map_entity_to_uri)]
    markdown_description: Annotated[str, Triple(PMDCAT.markdownDescription, PropertyStatus.recommended, map_str_to_markdown)]
    sparql_endpoint: Annotated[str, Triple(VOID.sparqlEndpoint, PropertyStatus.mandatory, URIRef)]
    family: Annotated[str, Triple(GDP.family, PropertyStatus.recommended, GDP.term)]
    update_due_on: Annotated[datetime, Triple(GDP.updateDueOn, PropertyStatus.recommended, Literal)]

    def __init__(self, uri: str):
        dcat.Dataset.__init__(self, uri)
        self.rdf_types.add(PMDCAT.Dataset)


class CatalogRecord(dcat.CatalogRecord):
    """HoldsCatalog Metadata."""

    metadata_graph: Annotated[str, Triple(PMDCAT.metadataGraph, PropertyStatus.mandatory, URIRef)]
    parent_catalog: Annotated[str, InverseTriple(DCAT.record, PropertyStatus.mandatory, URIRef)]
    """Catalog which this catalog record is contained within."""

    def __init__(self, uri: str, parent_catalog_uri: str):
        dcat.CatalogRecord.__init__(self, uri)
        self.parent_catalog = URIRef(parent_catalog_uri)


class Catalog(dcat.Catalog):
    """Represents an individual catalog."""

    def __init__(self, uri: str):
        dcat.Catalog.__init__(self, uri)
        self.rdf_types.add(PMDCAT.Catalog)
