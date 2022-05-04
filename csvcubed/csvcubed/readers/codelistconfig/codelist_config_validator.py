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

    def _flattern_concepts(
        self,
        concepts: list[CodeListConfigConcept],
    ) -> list[CodeListConfigConcept]:
        """
        TODO:Loads CSV-W metadata json-ld to rdflib graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        for concept in concepts:
            if concept.children:
                self._flattern_concepts(concept.children)
            self.flatterned_concepts.append(concept)

        return self.flatterned_concepts

    def _validate_sort_constraints(
        self, sort: CodeListConfigSort, concepts: list[CodeListConfigConcept]
    ):
        """
        TODO:Loads CSV-W metadata json-ld to rdflib graph

        Member of :class:`./MetadataProcessor`.

        :return: `Graph` - RDFLib Graph of CSV-W metadata json.
        """
        self._flattern_concepts(concepts)

        concepts_with_sort_order = [
            concept for concept in self.flatterned_concepts if concept.sort_order
        ]
        if sort and len(concepts_with_sort_order) > 0:
            raise Exception("Either the sort or concept's sort_order can be defined.")
        elif sort is None and len(concepts_with_sort_order) != len(
            self.flatterned_concepts
        ):
            raise Exception(
                "If the sort_order is defined for a one concept, it needs to be defined for all the concepts."
            )

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

    def validate_against_constraints(self, code_list_config: CodeListConfig):
        self._validate_sort_constraints(
            code_list_config.sort, code_list_config.concepts
        )
