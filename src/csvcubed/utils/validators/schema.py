import logging
import os
import re
from typing import Iterable, Union, Dict, List, Tuple
from textwrap import indent

import jsonschema
import jsonschema.exceptions

from csvcubed.utils.json import to_json_path
from csvcubed.utils.text import truncate
from csvcubed.models.jsonvalidationerrors import (
    JsonSchemaValidationError,
    AnyOfJsonSchemaValidationError,
)

log = logging.getLogger(__name__)


_indent = "    "


def validate_dict_against_schema(
    value: dict, schema: dict
) -> list[jsonschema.exceptions.ValidationError]:
    """
    Validates a dict against a schema.
    """
    try:
        # Validate our JSON document against the schema
        # This will implicitly validate the schema itself.
        v = jsonschema.Draft7Validator(schema)
        return list(sorted(v.iter_errors(value), key=lambda e: str(e.path)))
    except jsonschema.exceptions.ValidationError as err:
        log.error(f"Validation of the supplied config cube failed: {repr(err)}")
        raise err

    except jsonschema.exceptions.SchemaError as err:
        log.error(
            f"The schema provided for validation of the config cube was not a valid schema: {repr(err)}"
        )
        raise err

    except Exception as err:
        log.error(f"Unexpected Error: {repr(err)}")
        raise err


def map_to_internal_validation_errors(
    errors: List[jsonschema.exceptions.ValidationError],
) -> List[JsonSchemaValidationError]:
    """Maps from `jsonschema.exceptions.ValidationError` into our internal `JsonSchemaValidationError` models."""
    mapped_errors = []

    for error in errors:
        mapped_children = map_to_internal_validation_errors(error.context)
        if error.validator == "anyOf":
            # There are a series of options the user has to select between.
            # This code shows them the different options and which error messages are associated with them.
            mapped_errors.append(
                AnyOfJsonSchemaValidationError(
                    json_path=to_json_path(error.absolute_path),
                    message=error.message,
                    children=mapped_children,
                    possible_types_with_grouped_errors=_get_possible_types_with_grouped_errors(
                        error
                    ),
                )
            )
        else:
            mapped_errors.append(
                JsonSchemaValidationError(
                    json_path=to_json_path(error.absolute_path),
                    message=error.message,
                    children=mapped_children,
                )
            )

    return mapped_errors


def _get_possible_types_with_grouped_errors(
    error: jsonschema.exceptions.ValidationError,
) -> Iterable[Tuple[dict, List[JsonSchemaValidationError]]]:
    map_type_index_to_errors: Dict[
        int, List[jsonschema.exceptions.ValidationError]
    ] = {}
    for child_error in error.context:
        possible_type_id = list(child_error.relative_schema_path)[0]

        if possible_type_id not in map_type_index_to_errors:
            map_type_index_to_errors[possible_type_id] = []

        map_type_index_to_errors[possible_type_id].append(child_error)

    for (i, possible_type) in enumerate(error.validator_value):
        yield (
            possible_type,
            map_to_internal_validation_errors(map_type_index_to_errors[i]),
        )
