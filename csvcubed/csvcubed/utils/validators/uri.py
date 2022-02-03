"""
URI
---

pydantic validators for URIs.
"""
from typing import Optional

from pydantic import validator

from ..uri import ensure_looks_like_uri, ensure_values_in_lists_looks_like_uris


def validate_uri(attr_name: str, is_optional: bool = False) -> classmethod:
    """
    pydantic validator to ensure that an attribute has a string value which looks like a URI.

    example usage:

    .. code-block:: python

        class SomeModel(PydanticModel):
            some_uri: str

            _some_uri_validator = validate_uri("some_uri")
    """

    def validate(value: Optional[str]) -> Optional[str]:
        if value is not None and not is_optional:
            # If statement deals with pydantic bug - https://github.com/samuelcolvin/pydantic/issues/3741
            ensure_looks_like_uri(value)

        return value

    return validator(attr_name, allow_reuse=True, always=not is_optional)(validate)


def validate_uris_in_list(attr_name: str, is_optional: bool = False) -> classmethod:
    """
    pydantic validator to ensure that an attribute has a string value within lists, which also looks like a URI.

    example usage:

    .. code-block:: python

        class SomeModel(PydanticModel):
            some_uris: list[str]

            _some_uris_validator = validate_uri("some_uris")
    """

    def validate(values: Optional[list[str]]) -> Optional[list[str]]:
        if values is not None and not is_optional:
            # If statement deals with pydantic bug - https://github.com/samuelcolvin/pydantic/issues/3741
            ensure_values_in_lists_looks_like_uris(values)

        return values

    return validator(attr_name, allow_reuse=True, pre=True, always=not is_optional)(
        validate
    )
