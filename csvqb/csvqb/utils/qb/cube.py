"""
QbCube
------
"""
from typing import List, TypeVar, Type, Set

from csvqb.models.cube.qb.validationerrors import (
    CsvColumnLiteralWithUriTemplate,
    CsvColumnUriTemplateMissingError,
    MinNumComponentsNotSatisfiedError,
    MaxNumComponentsExceededError,
    WrongNumberComponentsError,
    UnitsNotDefinedError,
    BothUnitTypesDefinedError,
    IncompatibleComponentsError,
)
from csvqb.models.validationerror import ValidationError
from csvqb.models.cube.cube import Cube
from csvqb.models.cube.qb.columns import QbColumn
from csvqb.models.cube.qb.components.dimension import (
    QbDimension,
    ExistingQbDimension,
)
from csvqb.models.cube.qb.components.attribute import (
    QbAttribute,
    QbAttributeLiteral,
)
from csvqb.models.cube.qb.components.measure import QbMultiMeasureDimension, QbMeasure
from csvqb.models.cube.qb.components.unit import QbMultiUnits, QbUnit
from csvqb.models.cube.qb.components.observedvalue import (
    QbObservationValue,
    QbMultiMeasureObservationValue,
    QbSingleMeasureObservationValue,
)
from csvqb.models.cube.qb.components.datastructuredefinition import (
    ColumnarQbDataStructureDefinition,
)


QbColumnarDsdType = TypeVar(
    "QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition
)
"""Anything which inherits from :class:`ColumnarQbDataStructureDefinition 
    <csvqb.models.cube.qb.components.datastructuredefinition.ColumnarQbDataStructureDefinition>`."""


def get_columns_of_dsd_type(
    cube: Cube, t: Type[QbColumnarDsdType]
) -> List[QbColumn[QbColumnarDsdType]]:
    """
    e.g. `get_columns_of_dsd_type(cube, QbDimension)`

    :return: The :class:`QbColumn <csvqb.models.cube.qb.columns.QbColumn>` s in :obj:`cube` which have
        :attr:`components` of the requested type :obj:`t`.
    """
    return [
        c
        for c in cube.columns
        if isinstance(c, QbColumn) and isinstance(c.component, t)
    ]


def validate_qb_component_constraints(cube: Cube) -> List[ValidationError]:
    """
    Validate a :class:`QbCube` to highlight errors in configuration.

    :return: A list of :class:`ValidationError <csvqb.models.validationerror.ValidationError>` s.
    """

    errors = _validate_dimensions(cube)
    errors += _validate_attributes(cube)
    errors += _validate_observation_value_constraints(cube)
    return errors


def _validate_dimensions(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    dimension_columns = get_columns_of_dsd_type(cube, QbDimension)

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(c.component, ExistingQbDimension):
            if c.csv_column_uri_template is None:
                errors.append(
                    CsvColumnUriTemplateMissingError(
                        c.csv_column_title, ExistingQbDimension
                    )
                )

    if len(dimension_columns) == 0:
        errors.append(MinNumComponentsNotSatisfiedError(QbDimension, 1, 0))
    return errors


def _validate_attributes(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(c.component, QbAttribute):
            if (
                c.csv_column_uri_template is None
                and len(c.component.new_attribute_values) == 0  # type: ignore
            ):
                errors.append(
                    CsvColumnUriTemplateMissingError(
                        c.csv_column_title,
                        f"{c.component.__class__.__name__} using existing attribute values",
                    )
                )
        if isinstance(c, QbColumn) and isinstance(c.component, QbAttributeLiteral):
            if c.csv_column_uri_template is not None:
                errors.append(
                    CsvColumnLiteralWithUriTemplate(
                        c.csv_column_title,
                        f"{c.component.__class__.__name__} "
                        + "cannot have a uri_tempate as it holds literal values",
                    )
                )

    return errors


def _validate_observation_value_constraints(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    observed_value_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)

    if len(multi_units_columns) > 1:
        errors.append(
            MaxNumComponentsExceededError(QbMultiUnits, 1, len(multi_units_columns))
        )

    if len(observed_value_columns) != 1:
        errors.append(
            WrongNumberComponentsError(
                QbObservationValue, 1, len(observed_value_columns)
            )
        )
    else:
        single_measure_obs_val_columns = get_columns_of_dsd_type(
            cube, QbSingleMeasureObservationValue
        )
        multi_measure_obs_val_columns = get_columns_of_dsd_type(
            cube, QbMultiMeasureObservationValue
        )
        if len(multi_measure_obs_val_columns) == 1:
            obs_val_column = multi_measure_obs_val_columns[0]
            errors += _validate_observation_value(obs_val_column, multi_units_columns)
            errors += _validate_multi_measure_cube(cube, obs_val_column)
        elif len(single_measure_obs_val_columns) == 1:
            obs_val_column = single_measure_obs_val_columns[0]
            errors += _validate_observation_value(obs_val_column, multi_units_columns)
            errors += _validate_single_measure_cube(cube, obs_val_column)

    return errors


def _validate_multi_measure_cube(
    cube: Cube, obs_val_column: QbColumn[QbMultiMeasureObservationValue]
) -> List[ValidationError]:
    errors: List[ValidationError] = []

    multi_measure_columns = get_columns_of_dsd_type(cube, QbMultiMeasureDimension)
    if len(multi_measure_columns) == 0:
        errors.append(
            WrongNumberComponentsError(
                QbMultiMeasureDimension,
                expected_number=1,
                actual_number=0,
                additional_explanation="A multi-measure cube must have a measure dimension.",
            )
        )
    elif len(multi_measure_columns) > 1:
        errors.append(
            MaxNumComponentsExceededError(
                QbMultiMeasureDimension, 1, len(multi_measure_columns)
            )
        )

    return errors


def _validate_single_measure_cube(
    cube: Cube, obs_val_column: QbColumn[QbSingleMeasureObservationValue]
) -> List[ValidationError]:
    errors: List[ValidationError] = []

    multi_measure_columns = get_columns_of_dsd_type(cube, QbMultiMeasureDimension)
    if len(multi_measure_columns) > 0:
        errors.append(
            IncompatibleComponentsError(
                QbSingleMeasureObservationValue,
                QbMultiMeasureDimension,
                additional_explanation="A single-measure cube cannot have a measure dimension.",
            )
        )

    return errors


def _validate_observation_value(
    observation_value: QbColumn[QbObservationValue],
    multi_unit_columns: List[QbColumn[QbMultiUnits]],
) -> List[ValidationError]:
    errors: List[ValidationError] = []
    if observation_value.component.unit is None:
        if len(multi_unit_columns) == 0:
            errors.append(UnitsNotDefinedError())
    else:
        if len(multi_unit_columns) > 0:
            errors.append(BothUnitTypesDefinedError())

    return errors


def get_all_measures(cube: Cube) -> Set[QbMeasure]:
    """
    :return: The :obj:`set` of :class:`~csvqb.models.cube.qb.components.measure.QbMeasure` instances defined against the
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
    :return: The :obj:`set` of :class:`~csvqb.models.cube.qb.components.unit.QbUnit` instances defined against the
      cube's columns.
    """
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)
    obs_val_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    units = {unit for dim in multi_units_columns for unit in dim.component.units}
    units |= {x.component.unit for x in obs_val_columns if x.component.unit is not None}

    return units
