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
    EmptyQbMultiMeasureDimensionError,
    UriTemplateNameError
)
from csvcubed.models.cube.qb.components.validationerrors import (
    UndefinedMeasureUrisError,
    UndefinedUnitUrisError,
    UndefinedAttributeValueUrisError,
    ReservedUriValueError,
    ConflictingUriSafeValuesError,
    EmptyQbMultiUnitsError,
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

    _map = {
        BothMeasureTypesDefinedError: "Measures defined in multiple locations. Measures may only be defined in one location.",
        BothUnitTypesDefinedError: "Units defined in multiple locations. Units may only be defined in one location.",
        ColumnNotFoundInDataError: "Configuration found for column '{error.csv_column_title}' but no corresponding column found in CSV.",
        ColumnValidationError: (
            "An error occurred when validating the column '{error.csv_column_title}':{linesep}{error.error}"
        ),
        ConflictingUriSafeValuesError: "A URI collision has been detected in {_get_description_for_component(error.component_type)}.",
        CsvColumnUriTemplateMissingError: "The '{error.csv_column_name}' column definition is missing a 'cell_uri_template'; a suitable "
        "value could not be inferred.",
        DuplicateColumnTitleError: "There are multiple CSV columns with the title: '{error.csv_column_title}'.",
        EmptyQbMultiMeasureDimensionError: "A Measure column has been defined but no measures have been defined within it",
        EmptyQbMultiUnitsError: "A Unit column has been defined but no units have been defined within it",
        MoreThanOneObservationsColumnError: "Found {error.actual_number} observed values columns. Only 1 is permitted.",
        MoreThanOneMeasureColumnError: "Found {error.actual_number} measures columns. Only 1 is permitted.",
        MoreThanOneUnitsColumnError: "Found {error.actual_number} units columns. Only 1 is permitted.",
        MissingColumnDefinitionError: "Column '{error.csv_column_title}' is present in CSV but no configuration could be found.",
        NoDimensionsDefinedError: "The cube does not contain any dimensions, at least 1 dimension is required.",
        NoObservedValuesColumnDefinedError: "The cube does not contain an observed values column.",
        NoMeasuresDefinedError: "At least one measure must be defined in a cube.",
        NoUnitsDefinedError: "At least one unit must be defined in a cube.",
        ObservationValuesMissing: "Observed values missing in '{error.csv_column_title}' on rows: {error.row_numbers}",
        ReservedUriValueError: (
            "The URI value(s) {error.conflicting_values} conflict with the reserved value: "
            "{error.reserved_identifier}'."
        ),
        UnknownPydanticValidationError: (
            "An error was encountered when validating the cube. The error occurred in '{error.path}' "
            "and was reported as '{error.original_error}'"
        ),
        UndefinedAttributeValueUrisError: (
            "The Attribute URI(s) {error.undefined_values} in {_get_description_for_component(error.component)} "
            "have not been defined in the list of valid attribute values."
        ),
        UndefinedMeasureUrisError: "The Measure URI(s) {error.undefined_values} found in the data was not defined in the cube config.",
        UndefinedUnitUrisError: "The Unit URI(s) {error.undefined_values} found in the data was not defined in the cube config.",
        UriTemplateNameError: (
            'Uri template: {error.csv_column_uri_template} is referencing a column that is not defined in the config. '
            'Currently defined columns are: {error.column_names_concatenated}.'
        ),
        ValidationError: (
            "A validation error occurred when validating the cube: '{error.message}'."
        ),
    }

    message = _map.get(type(error))

    if not message:
        _logger.error("Unhandled validation error: %s", error)
        raise ValueError(f"Unhandled validation error type {type(error)}")

    # Lazy evaluation of f-string to account for differing attributes
    message = eval(f'f"{message}"')

    # for ConflictingUriSafeValuesError, extend the message with stringified
    # map of conflicting uris and labels
    if isinstance(error, ConflictingUriSafeValuesError):
        for (key, values) in error.map_uri_safe_values_to_conflicting_labels.items():
            vals = ", ".join([f"'{v}'" for v in values])
            message += f"{linesep}    The values {vals} map to the same URI-safe identifier '{key}'"

    if hasattr(error, "additional_explanation"):

        # dont run pyright on next line, not all error types have an additional_explanation
        additional_explanation = error.additional_explanation  # type: ignore

        if additional_explanation:
            message += f"{linesep}Further details: {additional_explanation}"

    return message


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
