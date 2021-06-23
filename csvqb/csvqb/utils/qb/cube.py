from typing import List, TypeVar, Type


from csvqb.models.validationerror import ValidationError
from csvqb.models.cube.cube import Cube
from csvqb.models.cube.qb.columns import QbColumn
from csvqb.models.cube.qb.components.dimension import QbDimension
from csvqb.models.cube.qb.components.measure import QbMultiMeasureTypes
from csvqb.models.cube.qb.components.observedvalue import QbObservationValue, QbMultiMeasureObservationValue, \
    QbSingleMeasureObservationValue
from csvqb.models.cube.qb.components.component import QbComponent


QbComponentType = TypeVar("QbComponentType", bound=QbComponent)


def get_columns_of_component_type(cube: Cube, t: Type[QbComponentType]) -> List[QbColumn[QbComponentType]]:
    return [c for c in cube.columns if isinstance(c, QbColumn) and isinstance(c.component, t)]


def validate_cube_qb_constraints(cube: Cube) -> List[ValidationError]:
    # assert validation specific to a cube-qb
    errors = _validate_dimensions(cube)
    errors += _validate_observation_value_constraints(cube)
    return errors


def _validate_dimensions(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    dimension_columns = get_columns_of_component_type(cube, QbDimension)
    if len(dimension_columns) == 0:
        errors.append(ValidationError("At least one dimension must be defined."))
    return errors


def _validate_observation_value_constraints(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    observed_value_columns = get_columns_of_component_type(cube, QbObservationValue)
    if len(observed_value_columns) != 1:
        errors.append(
            ValidationError(f"Found {len(observed_value_columns)} observation value columns. Expected 1."))
    else:
        single_measure_obs_val_columns = get_columns_of_component_type(cube, QbSingleMeasureObservationValue)
        multi_measure_obs_val_columns = get_columns_of_component_type(cube, QbMultiMeasureObservationValue)
        multi_measure_types_columns = get_columns_of_component_type(cube, QbMultiMeasureTypes)
        if len(multi_measure_obs_val_columns) == 1:
            if len(multi_measure_types_columns) == 0:
                errors.append(ValidationError(
                    f"Cube is defined as multi-measure but measure type column has not been specified."
                ))
            elif len(multi_measure_types_columns) > 1:
                errors.append(ValidationError("Multiple measure type columns have been defined."))
        elif len(single_measure_obs_val_columns) == 1:
            if len(multi_measure_types_columns) > 0:
                multi_measure_type_column_titles = \
                    ", ".join(["'" + c.csv_column_title + "'" for c in multi_measure_types_columns])
                errors.append(
                    ValidationError(f"Found multi-measure type column(s) {multi_measure_type_column_titles} in a "
                                    "single-measure cube.")
                  )

    return errors
