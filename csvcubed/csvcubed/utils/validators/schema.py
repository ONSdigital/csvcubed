import logging

import jsonschema
from jsonschema.exceptions import ValidationError, SchemaError

log = logging.getLogger(__name__)


def validate_dict_against_schema(value: dict, schema: dict) -> list[ValidationError]:
    """
    Validates a dict against a schema,
    """
    try:
        # Validate our schema against the standard 
        v = jsonschema.Draft7Validator(schema)
        return list(sorted(v.iter_errors(schema), key=lambda e: str(e.path)))
    except ValidationError as err:
        log.error(f"Validation of the supplied config cube failed: {repr(err)}")
        raise err

    except SchemaError as err:
        log.error(
            f"The schema provided for validation of the config cube was not a valid schema: {repr(err)}"
        )
        raise err

    except Exception as err:
        log.error(f"Unexpected Error: {repr(err)}")
        raise err
