import inspect
import logging
from os import linesep
from typing import Type, Union

from csvcubed.models.cube import (
    QbAttribute,
    QbCodeList,
    QbDimension,
    QbMultiUnits,
    QbMultiMeasureDimension,
    CsvColumnUriTemplateMissingError,
    NoDimensionsDefinedError,
    NoObservedValuesColumnDefinedError,
    NoMeasuresDefinedError,
    NoUnitsDefinedError,
    MoreThanOneObservationsColumnError,
    MoreThanOneMeasureColumnError,
    MoreThanOneUnitsColumnError,
    BothMeasureTypesDefinedError,
    BothUnitTypesDefinedError,
    ObservationValuesMissing,
    MissingColumnDefinitionError,
    DuplicateColumnTitleError,
    ColumnValidationError,
    ColumnNotFoundInDataError,
    QbObservationValue,
    QbStructuralDefinition,
)
from csvcubed.models.cube.qb.components.validationerrors import (
    UndefinedMeasureUrisError,
    UndefinedUnitUrisError,
    UndefinedAttributeValueUrisError,
    ReservedUriValueError,
    ConflictingUriSafeValuesError,
)
from csvcubed.models.validationerror import (
    ValidationError,
    UnknownPydanticValidationError,
)

_logger = logging.getLogger(__name__)


def friendly_error_mapping(error: ValidationError) -> str:
    """
    Given a validation error it returns an error message that is tailored to the qube-config.json interface so it's
     more user-friendly.
    """

    if isinstance(error, CsvColumnUriTemplateMissingError):
        return (
            f"The '{error.csv_column_name}' column definition is missing a 'cell_uri_template'; a suitable "
            f"value could not be inferred."
        )
    elif isinstance(error, NoDimensionsDefinedError):
        return "The cube does not contain any dimensions, at least 1 dimension is required."
    elif isinstance(error, NoObservedValuesColumnDefinedError):
        message = "The cube does not contain an observed values column."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, NoMeasuresDefinedError):
        message = "At least one measure must be defined in a cube."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, NoUnitsDefinedError):
        message = "At least one unit must be defined in a cube."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, MoreThanOneObservationsColumnError):
        message = (
            f"Found {error.actual_number} observed values columns. Only 1 is permitted."
        )
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, MoreThanOneMeasureColumnError):
        message = f"Found {error.actual_number} measures columns. Only 1 is permitted."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, MoreThanOneUnitsColumnError):
        message = f"Found {error.actual_number} units columns. Only 1 is permitted."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, BothMeasureTypesDefinedError):
        message = f"Measures defined in multiple locations. Measures may only be defined in one location."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, BothUnitTypesDefinedError):
        message = f"Units defined in multiple locations. Units may only be defined in one location."
        if error.additional_explanation:
            message += f"{linesep}Further details: {error.additional_explanation}"
        return message
    elif isinstance(error, ObservationValuesMissing):
        return f"Observed values missing in '{error.csv_column_title}' on rows: {error.row_numbers}"
    elif isinstance(error, MissingColumnDefinitionError):
        return f"Column '{error.csv_column_title}' is present in CSV but no configuration could be found."
    elif isinstance(error, DuplicateColumnTitleError):
        return f"There are multiple CSV columns with the title: '{error.csv_column_title}'."
    elif isinstance(error, ColumnValidationError):
        return (
            f"An error occurred when validating the column '{error.csv_column_title}':"
            + linesep
            + str(error.error)
        )
    elif isinstance(error, ColumnNotFoundInDataError):
        return f"Configuration found for column '{error.csv_column_title}' but no corresponding column found in CSV."
    elif isinstance(error, UnknownPydanticValidationError):
        return (
            f"An error was encountered when validating the cube. The error occurred in '{error.path}' "
            f"and was reported as '{error.original_error}'"
        )
    elif isinstance(error, UndefinedMeasureUrisError):
        return f"The Measure URI(s) {error.undefined_values} found in the data was not defined in the cube config."
    elif isinstance(error, UndefinedUnitUrisError):
        return f"The Unit URI(s) {error.undefined_values} found in the data was not defined in the cube config."
    elif isinstance(error, UndefinedAttributeValueUrisError):
        return (
            f"The Attribute URI(s) {error.undefined_values} in {_get_description_for_component(error.component)} "
            "have not been defined in the list of valid attribute values."
        )
    elif isinstance(error, ReservedUriValueError):
        return (
            f"The URI value(s) {error.conflicting_values} conflict with the reserved value: "
            f"{error.reserved_identifier}'."
        )
    elif isinstance(error, ConflictingUriSafeValuesError):
        message = f"A URI collision has been detected in {_get_description_for_component(error.component_type)}."
        for (key, values) in error.map_uri_safe_values_to_conflicting_labels.items():
            vals = ", ".join([f"'{v}'" for v in values])
            message += f"{linesep}    The values {vals} map to the same URI-safe identifier '{key}'"
        return message
    elif isinstance(error, ValidationError):
        return (
            f"A validation error occurred when validating the cube: '{error.message}'."
        )

    _logger.error("Unhandled validation error: %s", error)
    raise ValueError(f"Unhandled validation error type {type(error)}")


def _get_description_for_component(
    component: Union[QbStructuralDefinition, Type, str]
) -> str:
    _logger.debug("Getting description for component %s", component)

    if isinstance(component, str):
        return component
    elif isinstance(component, QbStructuralDefinition):
        if isinstance(component, QbMultiMeasureDimension):
            return f"the {component} measures column"
        elif isinstance(component, QbMultiUnits):
            return f"the {component} units column"
        if isinstance(component, QbAttribute):
            return f"the {component} attribute column"
        elif isinstance(component, QbDimension):
            return f"the {component} dimension column"
        elif isinstance(component, QbCodeList):
            return f"the {component} code list"
        elif isinstance(component, QbObservationValue):
            return f"the {component} observed values column"
    # else it is a type of component
    elif component == QbMultiMeasureDimension:
        return "a measures column"
    elif component == QbMultiUnits:
        return "a units column"
    elif inspect.isclass(component):
        if issubclass(component, QbAttribute):
            return "an attribute column"
        elif issubclass(component, QbDimension):
            return "a dimension column"
        elif issubclass(component, QbCodeList):
            return "a code list"
        elif issubclass(component, QbObservationValue):
            return "the observed values column"

    return f"a '{component}' component"
