"""
File
---

pydantic validators for files.
"""

from pydantic import validator
from pathlib import Path

from ..uri import ensure_looks_like_uri


def validate_file_exists(attr_name: str, is_optional: bool = False) -> classmethod:
    """
    pydantic validator to ensure that an attribute of type :obj:`pathutils.Path` has a value which always exists.

    example usage:

    .. code-block:: python

        class SomeModel(PydanticModel):
            some_uri: str

            _some_uri_validator = validate_uri("some_uri")
    """

    def ensure_exists(f: Path) -> None:
        if not f.exists():
            raise ValueError(f"Path '{f}' does not exist.")

    return validator(attr_name, allow_reuse=True, always=not is_optional)(ensure_exists)
