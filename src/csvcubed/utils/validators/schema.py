import logging
from typing import Dict, Iterable, List, Tuple

import jsonschema
import jsonschema.exceptions

from csvcubed.models.jsonvalidationerrors import (
    AnyOneOfJsonSchemaValidationError,
    GenericJsonSchemaValidationError,
    JsonSchemaValidationError,
)
from csvcubed.utils.json import to_json_path
from csvcubed.utils.log import debug_log_exception

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
    except jsonschema.exceptions.RefResolutionError as err:
        debug_log_exception(log, err)
        log.error(
            "Could not resolve schema dependency. You may have internet connectivity problems."
        )
        log.warning(
            "Unable to perform JSON Schema Validation. There may be undiscovered errors. Attempting to continue."
        )
        return []
    except Exception as err:
        log.error(f"Unexpected Error: {repr(err)}")
        raise err


def map_to_internal_validation_errors(
    schema: dict,
    errors: List[jsonschema.exceptions.ValidationError],
    use_relative_path: bool = False,
) -> List[JsonSchemaValidationError]:
    """Maps from `jsonschema.exceptions.ValidationError` into our internal `JsonSchemaValidationError` models."""
    mapped_errors = []

    for error in errors:
        json_path = to_json_path(
            error.relative_path if use_relative_path else error.absolute_path  # type: ignore
        )
        if error.validator in {"anyOf", "oneOf"}:
            mapped_errors.append(
                AnyOneOfJsonSchemaValidationError(
                    schema=schema,
                    json_path=json_path,
                    message=error.message,
                    possible_types_with_grouped_errors=list(
                        _get_possible_types_with_grouped_errors(schema, error)
                    ),
                    offending_value=error.instance,
                    schema_validator_type=error.validator,
                )
            )
        else:
            mapped_children = map_to_internal_validation_errors(
                schema, error.context or [], True
            )

            mapped_errors.append(
                GenericJsonSchemaValidationError(
                    schema=schema,
                    json_path=json_path,
                    message=error.message,
                    children=mapped_children,
                    offending_value=error.instance,
                    schema_validator_type=str(error.validator),
                )
            )

    return mapped_errors


def _get_possible_types_with_grouped_errors(
    schema: dict,
    error: jsonschema.exceptions.ValidationError,
) -> Iterable[Tuple[dict, List[JsonSchemaValidationError]]]:
    map_type_index_to_errors: Dict[
        int, List[jsonschema.exceptions.ValidationError]
    ] = {}

    child_errors = error.context or []
    for child_error in child_errors:
        possible_type_id = list(child_error.relative_schema_path)[0]

        if isinstance(possible_type_id, str):
            raise ValueError(f"Unexpected possible_type_id '{possible_type_id}'")

        if possible_type_id not in map_type_index_to_errors:
            map_type_index_to_errors[possible_type_id] = []

        map_type_index_to_errors[possible_type_id].append(child_error)

    for (i, possible_type) in enumerate(error.validator_value):
        if i in map_type_index_to_errors:
            yield (
                possible_type,
                map_to_internal_validation_errors(
                    schema, map_type_index_to_errors[i], True
                ),
            )
