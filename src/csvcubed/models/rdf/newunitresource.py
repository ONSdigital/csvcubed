"""
New Unit
--------
"""
from typing import Annotated, Optional

from csvcubedmodels.rdf.namespaces import OM2, QUDT, RDFS, XSD
from csvcubedmodels.rdf import (
    NewMetadataResource,
    Triple,
    PropertyStatus,
    map_resource_to_uri,
    map_to_literal_with_datatype,
    ExistingResource,
    MaybeResource,
)


class NewUnitResource(NewMetadataResource):
    """
    New RDF Resource representing a unit.

    Uses the OM2 & QUDT ontologies to define relationship with existing parent unit.
    """

    source_uri: Annotated[
        Optional[ExistingResource],
        Triple(RDFS.isDefinedBy, PropertyStatus.recommended, map_resource_to_uri),
    ]

    base_unit_uri: Annotated[
        MaybeResource["NewUnitResource"],
        Triple(OM2.hasUnit, PropertyStatus.optional, map_resource_to_uri),
        Triple(QUDT.isScalingOf, PropertyStatus.optional, map_resource_to_uri),
    ]

    base_unit_scaling_factor: Annotated[
        Optional[float],
        Triple(
            OM2.hasFactor,
            PropertyStatus.optional,
            map_to_literal_with_datatype(XSD.float),
        ),
    ]

    has_qudt_quantity_kind: Annotated[
        Optional[ExistingResource],
        Triple(QUDT.hasQuantityKind, PropertyStatus.optional, map_resource_to_uri),
    ]

    qudt_conversion_multiplier: Annotated[
        Optional[float],
        Triple(
            QUDT.conversionMultiplier,
            PropertyStatus.optional,
            map_to_literal_with_datatype(XSD.float),
        ),
    ]

    def __init__(self, uri: str):
        NewMetadataResource.__init__(self, uri)
        self.rdf_types.add(OM2.Unit)
        self.rdf_types.add(QUDT.Unit)
