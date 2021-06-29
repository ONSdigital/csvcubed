from .rdfresource import RdfResource
from sharedmodels.rdf.namespaces import RDF


class Class(RdfResource):
    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)
        self.rdf_types.add(RDF.Class)
