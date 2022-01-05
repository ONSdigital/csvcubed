"""
RDFS
--------------
"""
from csvcubedmodels.rdf.namespaces import RDFS

from .resource import NewResource


class Class(NewResource):
    def __init__(self, uri: str):
        NewResource.__init__(self, uri)
        self.rdf_types.add(RDFS.Class)
