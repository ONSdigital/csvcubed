import logging

from csvcubed.utils.validators.schema import validate_dict_against_schema
from csvcubed.models.codelistconfig.codelist_config import (
    CodeListConfig,
    CodeListConfigSort,
    CodeListConfigConcept,
)

_logger = logging.getLogger(__name__)


class CodeListConfigValidator:
    """
    TODO: description
    """

    flatterned_concepts: list[CodeListConfigConcept] = []

    def validate_against_schema(self, schema: dict, config: dict):
        """
        TODO:Loads CSV-W metadata json-ld to rdflib graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        schema_validation_errors = validate_dict_against_schema(
            value=config, schema=schema
        )

        if len(schema_validation_errors) > 0:
            raise Exception("".join(f"{err}," for err in schema_validation_errors))
