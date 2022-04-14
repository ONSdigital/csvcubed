from typing import TypeVar, Callable
from os import linesep

from csvcubed.models.validationerror import *
from csvcubed.models.cube.validationerrors import *
from csvcubed.models.cube.qb.validationerrors import *
from csvcubed.models.cube.qb.components.validationerrors import *

MSG_TEMPLATE: Dict[Type[ValidationError], Callable[[ValidationError], str]] = {  # type: ignore
    CsvColumnUriTemplateMissingError: lambda error:
        f"The '{error.csv_column_name}' column definition is missing a 'cell_uri_template'; a suitable"  # type: ignore
        " value could not be inferred.",
    NoDimensionsDefinedError: lambda error:
        "The cube does not contain any dimensions, at least 1 dimension is required.",
    NoObservedValuesColumnDefinedError: lambda error:
        "The cube does not contain an observed values column.{linesep}"
        f"Further details are: {error.additional_explanation}",  # type: ignore
    NoMeasuresDefinedError: lambda error:
        "At least one measure must be defined in a cube.{linesep}"
        f"Further details are: {error.additional_explanation}",  # type: ignore
    NoUnitsDefinedError: lambda error:
        f"At least one unit must be defined in a cube.{linesep}"
        f"Further details are: {error.additional_explanation}",  # type: ignore
    MoreThanOneObservationsColumnError: lambda error:
        f"Found {error.actual_number} observed values columns. Only 1 is permitted.{linesep}"  # type: ignore
        f"Further details are: {error.additional_explanation}",  # type: ignore
    MoreThanOneMeasureColumnError: lambda error:
        f"Found {error.actual_number} measures columns. Only 1 is permitted.{linesep}"  # type: ignore
        f"Further details are: {error.additional_explanation}",  # type: ignore
    MoreThanOneUnitsColumnError: lambda error:
        f"Found {error.actual_number} units columns. Only 1 is permitted.{linesep}"  # type: ignore
        f"Further details are: {error.additional_explanation}",  # type: ignore
    BothMeasureTypesDefinedError: lambda error:
        f"Measures defined in multiple locations. Measures may only be defined in one location.{linesep}"
        f"Further details are: {error.additional_explanation}",  # type: ignore
    BothUnitTypesDefinedError: lambda error:
        f"Units defined in multiple locations. Units may only be defined in one location.{linesep}"
        f"Further details are: {error.additional_explanation}",  # type: ignore
    ObservationValuesMissing: lambda error:
        f"Observed values missing in '{error.csv_column_title}' on rows: {error.row_numbers}",  # type: ignore
    MissingColumnDefinitionError: lambda error:
        f"Column '{error.csv_column_title}' is present in CSV but no configuration could be found.",  # type: ignore
    DuplicateColumnTitleError: lambda error:
        f"There are multiple CSV columns with the title: '{error.csv_column_title}'.",  # type: ignore
    ColumnValidationError: lambda error:
        (
            "An error occurred when validating the column '{error.csv_column_title}':" + linesep +  # type: ignore
            "{error.error]}"
        ),
    ColumnNotFoundInDataError: lambda error:
        f"Configuration found for column '{error.csv_column_title}' but no corresponding column "  # type: ignore
        f"found in CSV.",
    UnknownPydanticValidationError: lambda error:
        f"An error was encountered when validating the cube. The error occurred in '{error.path}' "  # type: ignore
        f"and was reported as '{error.original_error}'",  # type: ignore
    UndefinedMeasureUrisError: lambda error:
        f"The Measure URI {error.undefined_values} found in the data was not defined in the cube "  # type: ignore
        f"config.",
    UndefinedUnitUrisError: lambda error:
        f"The Unit URI {error.undefined_values} found in the data was not defined in the cube config.",  # type: ignore
    UndefinedAttributeValueUrisError: lambda error:
        f"The Attribute URI {error.undefined_values} in column '{error.component.label}' defined in the"  # type: ignore
        " cube config was not found in the data.",
    ReservedUriValueError: lambda error:
        f"The URI value(s) {error.conflicting_values} conflict with the reserved value: " # type: ignore
        f"'{error.reserved_identifier}'.",  # type: ignore
    ConflictingUriSafeValuesError: lambda error:
        f"A URI collision has been detected in: '{error.component_type}'.",  # type: ignore
    ValidationError: lambda error:
        f"A validation error occurred when validating the cube: '{error.message}'."  # type: ignore
}


def friendly_error_mapping(error: ValidationError) -> str:
    """
    Given an Exception / Error it returns an error message that is more user-friendly
    """
    msg = MSG_TEMPLATE[error.__class__](error)
    error_dict = error.as_dict()

    if isinstance(error, ConflictingUriSafeValuesError):
        error_dict['component'] = str(error_dict['component_type']).split('.')[-2].capitalize()
        for safe_uri, values in error.map_uri_safe_values_to_conflicting_labels.items():
            msg += f"{linesep}The values {tuple(values)} all map to the same identifier '{safe_uri}'."

    return msg.format(error=error_dict)
