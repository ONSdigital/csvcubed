"""
QbCube
------
"""
from typing import List, TypeVar, Type, Set

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.measure import (
    QbMultiMeasureDimension,
    QbMeasure,
)
from csvcubed.models.cube.qb.components.unit import QbMultiUnits, QbUnit
from csvcubed.models.cube.qb.components.observedvalue import (
    QbObservationValue,
    QbSingleMeasureObservationValue,
)
from csvcubed.models.cube.qb.components.datastructuredefinition import (
    ColumnarQbDataStructureDefinition,
)


QbColumnarDsdType = TypeVar(
    "QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition
)
"""Anything which inherits from :class:`ColumnarQbDataStructureDefinition 
    <csvcubed.models.cube.qb.components.datastructuredefinition.ColumnarQbDataStructureDefinition>`."""


def get_columns_of_dsd_type(
    cube: Cube, t: Type[QbColumnarDsdType]
) -> List[QbColumn[QbColumnarDsdType]]:
    """
    e.g. `get_columns_of_dsd_type(cube, QbDimension)`

    :return: The :class:`QbColumn <csvcubed.models.cube.qb.columns.QbColumn>` s in :obj:`cube` which have
        :attr:`components` of the requested type :obj:`t`.
    """
    return [
        c
        for c in cube.columns
        if isinstance(c, QbColumn) and isinstance(c.component, t)
    ]


def get_all_measures(cube: Cube) -> Set[QbMeasure]:
    """
    :return: The :obj:`set` of :class:`~csvcubed.models.cube.qb.components.measure.QbMeasure` instances defined against the
      cube's columns.
    """
    multi_measure_dimension_columns = get_columns_of_dsd_type(
        cube, QbMultiMeasureDimension
    )
    single_meas_obs_val_columns = get_columns_of_dsd_type(
        cube, QbSingleMeasureObservationValue
    )
    measures = {
        meas
        for dim in multi_measure_dimension_columns
        for meas in dim.component.measures
    }
    measures |= {x.component.measure for x in single_meas_obs_val_columns}

    return measures


def get_all_units(cube: Cube) -> Set[QbUnit]:
    """
    :return: The :obj:`set` of :class:`~csvcubed.models.cube.qb.components.unit.QbUnit` instances defined against the
      cube's columns.
    """
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)
    obs_val_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    units = {unit for dim in multi_units_columns for unit in dim.component.units}
    units |= {x.component.unit for x in obs_val_columns if x.component.unit is not None}

    return units
