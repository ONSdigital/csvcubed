from typing import List

from csvcubed.models.cube import (
    ObservationValuesMissing,
    QbMultiUnits,
    QbObservationValue,
    Cube,
    WrongNumberComponentsError,
    QbSingleMeasureObservationValue,
    QbMultiMeasureObservationValue,
    QbColumn,
    QbAttribute,
    ExistingQbAttribute,
    NewQbAttribute,
    QbMultiMeasureDimension,
    NoUnitsDefinedError,
    BothUnitTypesDefinedError,
    BothMeasureTypesDefinedError,
    MoreThanOneUnitsColumnError,
    MoreThanOneMeasureColumnError,
    NoMeasuresDefinedError,
    NoObservedValuesColumnDefinedError,
    MoreThanOneObservationsColumnError,
)

from csvcubed.models.cube.qb.components.measure import ExistingQbMeasure
from csvcubed.models.cube.qb.validationerrors import CsvColumnUriTemplateMissingError

from csvcubedmodels.rdf.namespaces import SDMX_Attribute

from csvcubed.models.validationerror import ValidationError
from csvcubed.utils.qb.cube import get_columns_of_dsd_type

SDMX_A_OBS_STATUS_URI: str = str(SDMX_Attribute.obsStatus)


def validate_observations(cube: Cube) -> List[ValidationError]:
    errors: List[ValidationError] = []
    observed_value_columns = get_columns_of_dsd_type(cube, QbObservationValue)
    multi_units_columns = get_columns_of_dsd_type(cube, QbMultiUnits)

    if len(multi_units_columns) > 1:
        errors.append(MoreThanOneUnitsColumnError(len(multi_units_columns)))

    num_obs_val_columns = len(observed_value_columns)
    if num_obs_val_columns == 0:
        errors.append(NoObservedValuesColumnDefinedError())
    elif num_obs_val_columns > 1:
        errors.append(MoreThanOneObservationsColumnError(num_obs_val_columns))
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

        errors += _validate_missing_observation_values(cube, observed_value_columns[0])

    return errors


def _validate_missing_observation_values(
    cube: Cube, observed_value_column: QbColumn[QbObservationValue]
) -> List[ValidationError]:
    """
    Check whether there are any missing observation values in this dataset. If there are, ensure they have at least one
    `sdmxa:obsStatus` set against them to explain why the value is missing.
    """

    if cube.data is None:
        return []

    potential_missing_values = cube.data[
        cube.data[observed_value_column.csv_column_title].isna()
    ]

    if potential_missing_values.size > 0:
        obs_status_columns = get_observation_status_columns(cube)
        for obs_status_column in obs_status_columns:
            potential_missing_values = potential_missing_values[
                potential_missing_values[obs_status_column.csv_column_title].isna()
            ]

        if potential_missing_values.size > 0:
            return [
                ObservationValuesMissing(
                    csv_column_title=observed_value_column.csv_column_title,
                    row_numbers=set(potential_missing_values.index),
                )
            ]

    return []


def get_observation_status_columns(cube: Cube) -> List[QbColumn[QbAttribute]]:
    """
    Returns any columns in the given cube which represent `sdmxa:obsStatus` attributes.
    """
    return [
        c
        for c in get_columns_of_dsd_type(cube, QbAttribute)
        if _attribute_represents_observation_status(c.structural_definition)
    ]


def _attribute_represents_observation_status(attribute: QbAttribute) -> bool:
    if isinstance(attribute, ExistingQbAttribute):
        # todo: There is no way currently to tell whether an existing attribute is a sub property of `sdmxa:obsStatus`
        #   once we've started to implement SPARQL querying/etc. we should check here to see if
        #   `attribute.attribute_uri` does extend `sdmxa:obsStatus`. Issue #273.
        return attribute.attribute_uri == SDMX_A_OBS_STATUS_URI
    elif isinstance(attribute, NewQbAttribute):
        return (
            attribute.parent_attribute_uri is not None
            # todo: There is no way currently to tell whether an existing attribute is a sub property of
            #  `sdmxa:obsStatus` once we've started to implement SPARQL querying/etc. we should check here to see
            #  if `attribute.parent_attribute_uri` does extend `sdmxa:obsStatus`. Issue #273.
            and attribute.parent_attribute_uri == SDMX_A_OBS_STATUS_URI
        )

    return False


def _validate_observation_value(
    observation_value: QbColumn[QbObservationValue],
    multi_unit_columns: List[QbColumn[QbMultiUnits]],
) -> List[ValidationError]:
    errors: List[ValidationError] = []
    if observation_value.structural_definition.unit is None:
        if len(multi_unit_columns) == 0:
            errors.append(NoUnitsDefinedError())
    else:
        if len(multi_unit_columns) > 0:
            errors.append(BothUnitTypesDefinedError())

    return errors


def _validate_multi_measure_cube(
    cube: Cube, obs_val_column: QbColumn[QbMultiMeasureObservationValue]
) -> List[ValidationError]:
    errors: List[ValidationError] = []

    multi_measure_columns: List[QbColumn[QbMultiMeasureDimension]] = get_columns_of_dsd_type(cube, QbMultiMeasureDimension)
    if len(multi_measure_columns) == 0:
        errors.append(NoMeasuresDefinedError())
    elif len(multi_measure_columns) > 1:
        errors.append(MoreThanOneMeasureColumnError(len(multi_measure_columns)))
    else:
        measure_column: QbColumn[QbMultiMeasureDimension] = multi_measure_columns[0]

        all_measures_existing = all(
            [
                isinstance(m, ExistingQbMeasure)
                for m in measure_column.structural_definition.measures
            ]
        )
    
        if all_measures_existing and measure_column.csv_column_uri_template is None:
                errors.append(
                    CsvColumnUriTemplateMissingError(
                        measure_column.csv_column_title, ExistingQbMeasure
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
            BothMeasureTypesDefinedError(
                f"{QbSingleMeasureObservationValue.__name__}.measure",
                QbMultiMeasureDimension,
                additional_explanation="A single-measure cube cannot have a measure dimension.",
            )
        )

    return errors
