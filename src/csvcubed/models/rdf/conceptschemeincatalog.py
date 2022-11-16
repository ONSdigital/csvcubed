"""
Concept Scheme In Catalog
-------------------------
"""

from csvcubedmodels.rdf import dcat, skos

from csvcubed.models.rdf import prov


class ConceptSchemeInCatalog(prov.Entity, skos.ConceptScheme, dcat.Dataset):
    """
    Represents both a skos:ConceptScheme and a dcat:Dataset in one node. Means that we don't have to link
    between the two.
    """

    def __init__(self, uri: str):
        prov.Entity.__init__(self, uri)
        skos.ConceptScheme.__init__(self, uri)
        dcat.Dataset.__init__(self, uri)
