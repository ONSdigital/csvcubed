import logging

from csvcubed.utils.validators.schema import validate_dict_against_schema
from csvcubed.models.codelistconfig.code_list_config import (
    CodeListConfigConcept,
)

_logger = logging.getLogger(__name__)


class CodeListConfigValidator:
    """
    Includes constaints for validating a code list json.
    """

    flatterned_concepts: list[CodeListConfigConcept] = []

    def validate_against_schema(self, schema: dict, config: dict):
        """
        Checks whether the code list config json conforms to the code list config schema.
        """
        schema_validation_errors = validate_dict_against_schema(
            value=config, schema=schema
        )

        if len(schema_validation_errors) > 0:
            raise Exception("".join(f"{err}," for err in schema_validation_errors))
