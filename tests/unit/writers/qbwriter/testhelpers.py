from copy import deepcopy
from typing import List

import pandas as pd
from csvcubedmodels import rdf

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.columns import CsvColumn
from csvcubed.utils.iterables import first


def get_standard_cube_for_columns(columns: List[CsvColumn]) -> Cube:
    data = pd.DataFrame(
        {
            "Country": ["Wales", "Scotland", "England", "Northern Ireland"],
            "Observed Value": [101.5, 56.2, 12.4, 77.8],
            "Marker": ["Provisional", "Provisional", "Provisional", "Provisional"],
        }
    )
    metadata: CatalogMetadata = CatalogMetadata("Cube Name")

    return Cube(deepcopy(metadata), data.copy(deep=True), columns)


def assert_component_defined(
    dataset: rdf.qb.DataSet, name: str
) -> rdf.qb.ComponentSpecification:
    component = first(
        dataset.structure.components,
        lambda x: str(x.uri) == f"cube-name.csv#component/{name}",
    )
    assert component is not None
    return component


def assert_component_property_defined(
    component: rdf.qb.ComponentSpecification, property_uri: str
) -> None:
    property = first(
        component.componentProperties, lambda x: str(x.uri) == property_uri
    )
    assert property is not None
    return property
