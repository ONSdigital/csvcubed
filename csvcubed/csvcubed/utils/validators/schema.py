import logging

import jsonschema
from jsonschema.exceptions import ValidationError


def validate_dict_against_schema(value: dict, schema: dict, log: logging.RootLogger) -> list[ValidationError]:
    """
    Validates a dict against a schema,
    """
    errors: list = []

    try:
        # Validate our schema against the standard  # TODO - confirm if required / parameterise ?
        v = jsonschema.Draft7Validator(schema)
        err = sorted(v.iter_errors(schema), key=lambda e: str(e.path))
        for error in err:
            errors.append(error)

        if errors:
            log.error(f"Schema validation failed for the base config schema: {errors}")
            return errors

        # Validate the cube config json against our the cube config schema
        errors = jsonschema.validate(value, schema)

    except jsonschema.exceptions.ValidationError as err:
        log.error(f"Validation of the supplied config cube failed: {repr(err)}")

    except jsonschema.exceptions.SchemaError as err:
        log.error(f"The schema provided for validation of the config cube was not a valid schema: {repr(err)}")

    except Exception as err:
        print(repr(err))

    return errors
