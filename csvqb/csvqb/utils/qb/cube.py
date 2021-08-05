"""
QbCube
------
"""
from typing import List, TypeVar, Type

from csvqb.models.cube.csvqb.validationerrors import (
    OutputUriTemplateMissingError,
    MinimumNumberOfComponentsError,
    MaximumNumberOfComponentsError,
    WrongNumberComponentsError,
    UnitsNotDefinedError,
    BothUnitTypesDefinedError,
    IncompatibleComponentsError,
)
from csvqb.models.validationerror import ValidationError
from csvqb.models.cube.cube import Cube
from csvqb.models.cube.csvqb.columns import QbColumn
from csvqb.models.cube.csvqb.components.dimension import (
    QbDimension,
    ExistingQbDimension,
)
from csvqb.models.cube.csvqb.components.attribute import (
    ExistingQbAttribute,
    QbAttribute,
)
from csvqb.models.cube.csvqb.components.measure import QbMultiMeasureDimension
from csvqb.models.cube.csvqb.components.unit import QbMultiUnits
from csvqb.models.cube.csvqb.components.observedvalue import (
    QbObservationValue,
    QbMultiMeasureObservationValue,
    QbSingleMeasureObservationValue,
)
from csvqb.models.cube.csvqb.components.datastructuredefinition import (
    ColumnarQbDataStructureDefinition,
)


QbColumnarDsdType = TypeVar(
    "QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition
)


def get_columns_of_dsd_type(
    cube: Cube, t: Type[QbColumnarDsdType]
) -> List[QbColumn[QbColumnarDsdType]]:
    return [
        c
        for c in cube.columns
        if isinstance(c, QbColumn) and isinstance(c.component, t)
    ]


def validate_qb_component_constraints(cube: Cube) -> List[ValidationError]:
    # assert validation specific to a cube-qb

    errors = _validate_dimensions(cube)
    errors += _validate_attributes(cube)
    errors += _validate_observation_value_constraints(cube)
    return errors


def _validate_dimensions(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    dimension_columns = get_columns_of_dsd_type(cube, QbDimension)

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(c.component, ExistingQbDimension):
            if c.output_uri_template is None:
                errors.append(
                    OutputUriTemplateMissingError(
                        c.csv_column_title, ExistingQbDimension
                    )
                )

    if len(dimension_columns) == 0:
        errors.append(MinimumNumberOfComponentsError(QbDimension, 1, 0))
    return errors


def _validate_attributes(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(c.component, QbAttribute):
            if (
                c.output_uri_template is None
                and len(c.component.new_attribute_values) == 0  # type: ignore
            ):
                errors.append(
                    ValidationError(
                        f"'{c.csv_column_title}' - a QbAttribute using existing attribute values must have an "
                        f"output_uri_template defined."
                    )
                )

    return errors


def _validate_observation_value_constraints(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    observed_value_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)

    if len(multi_units_columns) > 1:
        errors.append(
            MaximumNumberOfComponentsError(QbMultiUnits, 1, len(multi_units_columns))
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
            MaximumNumberOfComponentsError(
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
                additional_explanation="A single measure cube cannot have a measure dimension.",
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
