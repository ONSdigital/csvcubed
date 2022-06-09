"""
File
---

pydantic validators for files.
"""
import logging
from typing import Optional

from pydantic import validator
from pathlib import Path


_logger = logging.getLogger(__name__)


def validate_file_exists(attr_name: str, is_optional: bool = False) -> classmethod:
    """
    pydantic validator to ensure that an attribute of type :obj:`pathutils.Path` has a value which always exists.

    example usage:

    .. code-block:: python

        class SomeModel(PydanticModel):
            some_uri: str

            _some_uri_validator = validate_uri("some_uri")
    """

    def ensure_exists(f: Optional[Path]) -> Optional[Path]:
        if f is not None and not is_optional:
            # If statement deals with pydantic bug - https://github.com/samuelcolvin/pydantic/issues/3741
            if not f.exists():
                raise ValueError(f"Path '{f}' does not exist.")

            _logger.debug("Path '%s' exists.", f)

        return f

    return validator(attr_name, allow_reuse=True, always=not is_optional)(ensure_exists)
