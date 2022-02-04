"""
Attributes
----------

pydantic validators for class attributes.
"""
import logging
from typing import Any, Dict, List
from pydantic import root_validator


_logger = logging.getLogger(__name__)


def enforce_optional_attribute_dependencies(
    map_attribute_name_to_dependent_attributes: Dict[str, List[str]]
) -> classmethod:
    """
    pydantic **root** validator to ensure that optional attributes are provided with their dependencies or not
    provided at all.
    """

    def ensure_dependencies_present(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for (
            attribute_name,
            dependent_attribute_names,
        ) in map_attribute_name_to_dependent_attributes.items():
            val = values.get(attribute_name)
            if val is not None:
                missing_values = []
                for a in dependent_attribute_names:
                    dependent_val = values.get(a)
                    if dependent_val is None:
                        missing_values.append(a)

                if len(missing_values) > 0:
                    missing_values_str = ", ".join([f"'{v}'" for v in missing_values])
                    raise ValueError(
                        f"'{attribute_name}' has been specified, but the following is missing and must be "
                        f"provided: {missing_values_str}."
                    )

                _logger.debug(
                    "Attribute '%s' has dependent attributes %s satisfied.",
                    attribute_name,
                    dependent_attribute_names,
                )

        return values

    return root_validator(ensure_dependencies_present, allow_reuse=True)  # type: ignore
