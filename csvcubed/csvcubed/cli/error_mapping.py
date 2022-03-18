from csvcubed.models.validationerror import *
from csvcubed.models.cube.validationerrors import *
from csvcubed.models.cube.qb.validationerrors import *
from csvcubed.models.cube.qb.components.validationerrors import *


def friendly_error_mapping(error: ValidationError) -> str:
    """
    Given an Exception / Error it returns an error message that is more user-friendly
    """
    if error.__class__.__name__ not in [
        'ValidationError',
        'UnknownPydanticValidationError',
        'ColumnNotFoundInDataError',
        'ColumnValidationError',
        'DuplicateColumnTitleError',
        'MissingColumnDefinitionError',
        'ObservationValuesMissing',
        'BothUnitTypesDefinedError',
        'BothMeasureTypesDefinedError',
        'NoUnitsDefinedError',
        'NoMeasuresDefinedError',
        'NoObservedValuesColumnDefinedError',
        'LabelUriCollisionError',
        'UndefinedMeasureUrisError',
        'UndefinedUnitUrisError',
        'UndefinedAttributeValueUrisError',
        'ReservedUriValueError',
        'ConflictingUriSafeValuesError',
        'CsvColumnUriTemplateMissingError',
        'MoreThanOneObservationsColumnError',
        'MoreThanOneMeasureColumnError',
        'MoreThanOneUnitsColumnError',
    ]:
        return str(error.message)

    if isinstance(error, CsvColumnUriTemplateMissingError):
        msg = f"An error occurred as {error.component_type} column: '{error.csv_column_name}' requires a URI Template to be defined in the " \
              f"cube config json as it cannot infer its own."

    elif isinstance(error, NoObservedValuesColumnDefinedError):
        msg = f"The cube does not contain an Observed Values column, this column type is required."

    elif isinstance(error, NeitherDefinedError):
        if isinstance(error, NoMeasuresDefinedError):
            msg = "No column of measures was found in the cube."

        elif isinstance(error, NoUnitsDefinedError):
            msg = "No column of units was found in the cube."

    elif isinstance(error, MaxNumComponentsExceededError):
        if isinstance(error, MoreThanOneObservationsColumnError):
            msg = f"The cube contained {error.actual_number} columns of Observation values, only 1 is permitted."

        elif isinstance(error, MoreThanOneMeasureColumnError):
            msg = f"The cube contained {error.actual_number} columns of Measures, only 1 is permitted."

        elif isinstance(error, MoreThanOneUnitsColumnError):
            msg = f"The cube contained {error.actual_number} columns of Units, only 1 is permitted."

    elif isinstance(error, IncompatibleComponentsError):
        if isinstance(error, BothMeasureTypesDefinedError):
            msg = f"Both measure types were present in the cube. \n" \
                  f"The columns are '{error.component_one}' and '{error.component_two}' "

        elif isinstance(error, BothUnitTypesDefinedError):
            msg = f"Both unit types were present in the cube. \n" \
                  f"The columns are '{error.component_one}' and '{error.component_two}' "

    elif isinstance(error, ObservationValuesMissing):
        msg = f"Observation values are missing in the column: '{error.csv_column_title}' " \
              f"on rows: {error.row_numbers}"

    elif isinstance(error, MissingColumnDefinitionError):
        msg = f"The column '{error.csv_column_title}' is present in the data but does not have " \
              f"a configuration in the cube config. "

    elif isinstance(error, DuplicateColumnTitleError):
        msg = f"There are multiple columns with the column title: '{error.csv_column_title}'."

    elif isinstance(error, ColumnValidationError):
        msg = f"An error was encountered whilst validating the column '" \
              f"{error.csv_column_title}'. \n" \
              f"The error was: '{error.error}'"

    elif isinstance(error, ColumnNotFoundInDataError):
        msg = f"The cube configuration refers to the column '{error.csv_column_title}' " \
               f"but no column in the data has this title."

    elif isinstance(error, UnknownPydanticValidationError):
        msg = f"An error was encountered when validating the cube's data structures. " \
              f"The error occurred in '{error.path}' and was reported as '{error.original_error}'"

    elif isinstance(error, LabelUriCollisionError):
        msg = f"A label-uri collision error occurred when validating the cube: '{error.message}'.  The column: '" \
              f"{error.csv_column_name}' with URI: '{error.conflicting_identifier}' conflicted with the values: '" \
              f"{error.conflicting_values}'"

    elif isinstance(error, UndefinedValuesError):
        if isinstance(error, UndefinedMeasureUrisError):
            msg = f"The Measure URI {error.undefined_values} found in the data was not defined in the cube config."

        elif isinstance(error, UndefinedUnitUrisError):
            msg = f"The Unit URI {error.undefined_values} found in the data was not defined in the cube config."

        elif isinstance(error, UndefinedAttributeValueUrisError):
            msg = f"The Attribute URI {error.undefined_values} in column '{error.component.label}' " \
               "defined in the cube config was not found in the data."

    elif isinstance(error, PydanticThrowableSpecificValidationError):
        if isinstance(error, ReservedUriValueError):
            msg = f"A Reserved-URI Value error occurred when validating the cube, {error.message}.  The URI value(s) of " \
                  f"'{error.conflicting_values}' conflicted with the reserved value: '{error.reserved_identifier}' " \
                  f"in the code list values."

        elif isinstance(error, ConflictingUriSafeValuesError):
            msg = f"Conflicting safe URI values were found when validating the cube, in '" \
                  f"{str(error.component_type).split('.')[-2].capitalize()}' column '" \
                  f"{error.path[2].replace('_', ' ')}'"

            for safe_uri, values in error.map_uri_safe_values_to_conflicting_labels.items():
                msg += f"\nThe values {values} all have the same safe-uri of '{safe_uri}' and the column labels " \
                       f"were: {list(error.map_uri_safe_values_to_conflicting_labels.keys())}."

    elif isinstance(error, ValidationError):
        msg = f"A validation error occurred when validating the cube: '{error.message}'."

    if hasattr(error, 'additional_explanation') and error.additional_explanation:
        msg += f"\nFurther details are: {error.additional_explanation}"

    if hasattr(error, 'get_error_url'):
        msg += f"\nRefer to {error.get_error_url()} for guidance on correcting this problem."

    return msg