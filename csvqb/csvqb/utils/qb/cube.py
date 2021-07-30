from typing import List, TypeVar, Type


from csvqb.models.validationerror import ValidationError
from csvqb.models.cube.cube import Cube
from csvqb.models.cube.csvqb.columns import QbColumn
from csvqb.models.cube.csvqb.components.dimension import QbDimension, ExistingQbDimension
from csvqb.models.cube.csvqb.components.measure import QbMultiMeasureDimension
from csvqb.models.cube.csvqb.components.unit import QbMultiUnits
from csvqb.models.cube.csvqb.components.observedvalue import QbObservationValue, QbMultiMeasureObservationValue, \
    QbSingleMeasureObservationValue
from csvqb.models.cube.csvqb.components.datastructuredefinition import ColumnarQbDataStructureDefinition


QbColumnarDsdType = TypeVar("QbColumnarDsdType", bound=ColumnarQbDataStructureDefinition)


def get_columns_of_dsd_type(cube: Cube, t: Type[QbColumnarDsdType]) -> List[QbColumn[QbColumnarDsdType]]:
    return [c for c in cube.columns if isinstance(c, QbColumn) and isinstance(c.component, t)]


def validate_qb_component_constraints(cube: Cube) -> List[ValidationError]:
    # assert validation specific to a cube-qb

    errors = _validate_dimensions(cube)
    errors += _validate_observation_value_constraints(cube)
    return errors


def _validate_dimensions(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    dimension_columns = get_columns_of_dsd_type(cube, QbDimension)

    for c in cube.columns:
        if isinstance(c, QbColumn) and isinstance(c.component, ExistingQbDimension):
            if c.output_uri_template is None:
                errors.append(
                    ValidationError(f"'{c.csv_column_title}' - an ExistingQbDimension must have an output_uri_template "
                                    "defined."))

    if len(dimension_columns) == 0:
        errors.append(ValidationError("At least one dimension must be defined."))
    return errors


def _validate_observation_value_constraints(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    observed_value_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)

    if len(multi_units_columns) > 1:
        errors.append(ValidationError(f"Found {len(multi_units_columns)} units columns. Expected maximum 1."))

    if len(observed_value_columns) != 1:
        errors.append(ValidationError(f"Found {len(observed_value_columns)} observation value columns. Expected 1."))
    else:
        single_measure_obs_val_columns = get_columns_of_dsd_type(cube, QbSingleMeasureObservationValue)
        multi_measure_obs_val_columns = get_columns_of_dsd_type(cube, QbMultiMeasureObservationValue)
        if len(multi_measure_obs_val_columns) == 1:
            obs_val_column = multi_measure_obs_val_columns[0]
            errors += _validate_observation_value(obs_val_column, multi_units_columns)
            errors += _validate_multi_measure_cube(cube, obs_val_column)
        elif len(single_measure_obs_val_columns) == 1:
            errors += _validate_observation_value(single_measure_obs_val_columns[0], multi_units_columns)

    return errors


def _validate_multi_measure_cube(cube: Cube,
                                 obs_val_column: QbColumn[QbMultiMeasureObservationValue]) -> List[ValidationError]:
    errors: List[ValidationError] = []

    multi_measure_columns = get_columns_of_dsd_type(cube, QbMultiMeasureDimension)
    if len(multi_measure_columns) == 0:
        errors.append(ValidationError("No multi-measure column found in multi-measure cube."))
    elif len(multi_measure_columns) > 1:
        errors.append(
            ValidationError(f"Found {len(multi_measure_columns)} measure dimension columns defined. Expected 1.")
        )

    return errors


def _validate_single_measure_cube(cube: Cube,
                                  obs_val_column: QbColumn[QbSingleMeasureObservationValue]) -> List[ValidationError]:
    errors: List[ValidationError] = []

    multi_measure_columns = get_columns_of_dsd_type(cube, QbMultiMeasureDimension)
    if len(multi_measure_columns) > 0:
        errors.append(
            ValidationError(f"Found {len(multi_measure_columns)} measure dimension columns in single measure cube.")
        )

    return errors


def _validate_observation_value(observation_value: QbColumn[QbObservationValue],
                                multi_unit_columns: List[QbColumn[QbMultiUnits]]) -> List[ValidationError]:
    errors: List[ValidationError] = []
    if observation_value.component.unit is None:
        if len(multi_unit_columns) == 0:
            errors.append(
                ValidationError(
                    f"{observation_value.component} must have either a defined unit, or a units column must be defined."
                )
            )
    else:
        if len(multi_unit_columns) > 0:
            errors.append(
                ValidationError(
                    f"{observation_value.component} has a unit and a units column is also defined."
                )
            )

    return errors
