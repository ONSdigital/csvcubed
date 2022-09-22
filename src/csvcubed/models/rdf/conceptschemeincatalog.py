"""
Concept Scheme In Catalog
-------------------------
"""
from typing import Annotated

from csvcubedmodels.rdf import dcat, skos

from csvcubed.models.rdf import prov

# activity = prov_Activity("#activity-uri")
# activity.used = ExistingResource("http://github.com/v0.1.4")

# entity = prov_Entity("#code-list-identi")
# entity.was_generated_by = activity


class ConceptSchemeInCatalog(prov.Entity, skos.ConceptScheme, dcat.Dataset):
    """
    Represents both a skos:ConceptScheme and a dcat:Dataset in one node. Means that we don't have to link
    between the two.
    """

    def __init__(self, uri: str):
        prov.Entity.__init__(self, uri)
        skos.ConceptScheme.__init__(self, uri)
        dcat.Dataset.__init__(self, uri)
