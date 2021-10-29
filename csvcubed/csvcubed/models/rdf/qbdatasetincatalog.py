"""
qb:DataSet in Catalog
---------------------
"""
from csvcubedmodels.rdf import dcat, qb


class QbDataSetInCatalog(qb.DataSet, dcat.Dataset):
    """
    Represents both a qb:DataSet and a dcat:Dataset in one node. Means that we don't have to link
    between the two.
    """

    def __init__(self, uri: str):
        qb.DataSet.__init__(self, uri)
        dcat.Dataset.__init__(self, uri)
