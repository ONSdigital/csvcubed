from copy import deepcopy
from typing import List

import pandas as pd
from sharedmodels.rdf import qb

from csvqb.models.cube import *
from csvqb.tests.unit.unittestbase import UnitTestBase
from csvqb.utils.iterables import first
from csvqb.writers.qbwriter import _generate_qb_dataset_dsd_definitions


def _get_standard_cube_for_columns(columns: List[CsvColumn]) -> Cube:
    data = pd.DataFrame({
        "Country": ["Wales", "Scotland", "England", "Northern Ireland"],
        "Observed Value": [101.5, 56.2, 12.4, 77.8],
        "Marker": ["Provisional", "Provisional", "Provisional", "Provisional"]
    })
    metadata: CubeMetadata = CubeMetadata("Some qube")

    return Cube(deepcopy(metadata), data.copy(deep=True), columns)


def _assert_component_defined(dataset: qb.DataSet, name: str) -> qb.ComponentSpecification:
    component = first(dataset.structure.components, lambda x: str(x.uri) == f"#component/{name}")
    assert(component is not None)
    return component


def _assert_component_property_defined(component: qb.ComponentSpecification, property_uri: str) -> None:
    property = first(component.componentProperties, lambda x: str(x.uri) == property_uri)
    assert(property is not None)
    return property


class QbWriterTests(UnitTestBase):
    def test_structure_defined(self):
        cube = _get_standard_cube_for_columns([
            QbColumn("Country", ExistingQbDimension("http://example.org/dimensions/country")),
            QbColumn("Marker", ExistingQbAttribute("http://example.org/attributes/marker")),
            QbColumn("Observed Value", QbSingleMeasureObservationValue(
                ExistingQbMeasure("http://example.org/units/some-existing-measure"),
                ExistingQbUnit("http://example.org/units/some-existing-unit")))
        ])

        dataset = _generate_qb_dataset_dsd_definitions(cube)

        self.assertIsNotNone(dataset)

        self.assertIsNotNone(dataset.structure)
        self.assertIsInstance(dataset.structure, qb.DataStructureDefinition)

        self.assertIsNotNone(dataset.structure.componentProperties)

        _assert_component_defined(dataset, "country")
        _assert_component_defined(dataset, "marker")
        _assert_component_defined(dataset, "some-existing-unit")
        _assert_component_defined(dataset, "some-existing-measure")
