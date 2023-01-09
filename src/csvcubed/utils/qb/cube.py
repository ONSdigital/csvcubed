"""
QbCube
------

Utilities for getting columns (of a given type) from the `qb:DataStructureType`
"""
import logging
from typing import List, Set, TypeVar

from csvcubed.models.cube.cube import Cube
from csvcubed.models.cube.cube_shape import CubeShape
from csvcubed.models.cube.qb.components import (
    QbColumnStructuralDefinition,
    QbMeasure,
    QbMultiMeasureDimension,
    QbMultiUnits,
    QbObservationValue,
    QbUnit,
)

_logger = logging.getLogger(__name__)


QbColumnarDsdType = TypeVar("QbColumnarDsdType", bound=QbColumnStructuralDefinition)
"""Anything which inherits from :class:`ColumnarQbDataStructureDefinition 
    <csvcubed.models.cube.qb.components.datastructuredefinition.ColumnarQbDataStructureDefinition>`."""


def get_all_measures(cube: Cube) -> Set[QbMeasure]:
    """
    :return: The :obj:`set` of :class:`~csvcubed.models.cube.qb.components.measure.QbMeasure` instances defined against the
      cube's columns.
    """
    multi_measure_dimension_columns = cube.get_columns_of_dsd_type(
        QbMultiMeasureDimension
    )
    obs_val_columns = cube.get_columns_of_dsd_type(QbObservationValue)
    pivoted_obs_vals: List[QbObservationValue] = [
        c.structural_definition
        for c in obs_val_columns
        if c.structural_definition.is_pivoted_shape_observation
    ]

    measures: Set[QbMeasure] = {
        meas
        for dim in multi_measure_dimension_columns
        for meas in dim.structural_definition.measures
    }
    measures |= {o.measure for o in pivoted_obs_vals}  # type: ignore

    _logger.debug("Discovered measures %s", measures)
    return measures


def get_all_units(cube: Cube) -> Set[QbUnit]:
    """
    :return: The :obj:`set` of :class:`~csvcubed.models.cube.qb.components.unit.QbUnit` instances defined against the
      cube's columns.
    """
    multi_units_columns = cube.get_columns_of_dsd_type(QbMultiUnits)
    obs_val_columns = cube.get_columns_of_dsd_type(QbObservationValue)
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


def detect_shape_of_cube(cube: Cube) -> CubeShape:
    """
    Given a cube as input, returns the shape of that cube (Standard or Pivoted)
    """
    obs_val_columns = cube.get_columns_of_dsd_type(QbObservationValue)

    all_pivoted = True
    all_standard_shape = True
    for obs_val_col in obs_val_columns:
        all_pivoted = (
            all_pivoted
            and obs_val_col.structural_definition.is_pivoted_shape_observation
        )
        all_standard_shape = (
            all_standard_shape
            and not obs_val_col.structural_definition.is_pivoted_shape_observation
        )

    if all_pivoted:
        return CubeShape.Pivoted
    elif all_standard_shape:
        return CubeShape.Standard
    else:
        raise TypeError(
            "The input metadata is invalid as the shape of the cube it represents is not supported. More specifically, the input contains some observation values that are pivoted and some are not pivoted."
        )
