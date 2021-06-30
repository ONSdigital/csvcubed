from rdflib import RDF


from .rdfresource import RdfResource


class Class(RdfResource):
    def __init__(self, uri: str):
        RdfResource.__init__(self, uri)
        self.rdf_types.add(RDF.Class)
