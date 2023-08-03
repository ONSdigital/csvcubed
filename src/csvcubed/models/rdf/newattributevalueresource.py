"""
New Attribute Value
-------------------
"""
from typing import Annotated, Optional

import csvcubedmodels.rdf.rdfs as rdfs
from csvcubedmodels.rdf import (
    ExistingResource,
    MaybeResource,
    NewMetadataResource,
    PropertyStatus,
    Triple,
    map_resource_to_uri,
)
from csvcubedmodels.rdf.namespaces import QB, RDFS, SKOS
from csvcubedmodels.rdf.qb import AttributeProperty, CodedProperty, ComponentProperty


class NewAttributeValueResource(NewMetadataResource):
    """
    New RDF Resource representing a value that an attribute can take.
    """

    source_uri: Annotated[
        Optional[ExistingResource],
        Triple(RDFS.isDefinedBy, PropertyStatus.recommended, map_resource_to_uri),
    ]

    parent_attribute_value_uri: Annotated[
        MaybeResource["NewAttributeValueResource"],
        Triple(SKOS.broader, PropertyStatus.recommended, map_resource_to_uri),
    ]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)


class CodedAttributeProperty(CodedProperty, AttributeProperty):
    """Attribute with code list property - The class of components which represent attributes of observations in the cube,
    e.g. observation status, which have code lists associated with them"""

    def __init__(self, uri: str):
        CodedProperty.__init__(self, uri)
        ComponentProperty.__init__(self, uri)
        self.rdf_types.add(QB.AttributeProperty)
