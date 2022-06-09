"""
Concept Scheme In Catalog
-------------------------
"""
from csvcubedmodels.rdf import dcat, skos


class ConceptSchemeInCatalog(skos.ConceptScheme, dcat.Dataset):
    """
    Represents both a skos:ConceptScheme and a dcat:Dataset in one node. Means that we don't have to link
    between the two.
    """

    def __init__(self, uri: str):
        skos.ConceptScheme.__init__(self, uri)
        dcat.Dataset.__init__(self, uri)
