"""
QbCube
------

Utilities for getting columns (of a given type) from the `qb:DataStructureType`
"""
import logging
from typing import List, TypeVar, Type, Set

from csvcubed.models.cube import (
    Cube,
    QbColumn,
    QbMeasure,
    QbMultiMeasureDimension,
    QbMultiUnits,
    QbUnit,
    QbObservationValue,
    QbSingleMeasureObservationValue,
    QbColumnStructuralDefinition,
)


_logger = logging.getLogger(__name__)


QbColumnarDsdType = TypeVar("QbColumnarDsdType", bound=QbColumnStructuralDefinition)
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
    columns_of_type = [
        c
        for c in cube.columns
        if isinstance(c, QbColumn) and isinstance(c.structural_definition, t)
    ]

    _logger.debug("Found columns of type %s: %s", t, columns_of_type)

    return columns_of_type


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
    measures: Set[QbMeasure] = {
        meas
        for dim in multi_measure_dimension_columns
        for meas in dim.structural_definition.measures
    }
    measures |= {x.structural_definition.measure for x in single_meas_obs_val_columns}

    _logger.debug("Discovered measures %s", measures)
    return measures


def get_all_units(cube: Cube) -> Set[QbUnit]:
    """
    :return: The :obj:`set` of :class:`~csvcubed.models.cube.qb.components.unit.QbUnit` instances defined against the
      cube's columns.
    """
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)
    obs_val_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    units: Set[QbUnit] = {
        unit for dim in multi_units_columns for unit in dim.structural_definition.units
    }
    units |= {
        x.structural_definition.unit
        for x in obs_val_columns
        if x.structural_definition.unit is not None
    }

    _logger.debug("Discovered units %s", units)
    return units
