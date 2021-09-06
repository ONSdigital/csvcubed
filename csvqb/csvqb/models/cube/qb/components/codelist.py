"""
Code Lists
----------
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Set
from abc import ABC
from pydantic import root_validator

from csvqb.models.uriidentifiable import UriIdentifiable
from csvqb.readers.skoscodelistreader import (
    extract_code_list_concept_scheme_info,
)
from .arbitraryrdf import ArbitraryRdf, RdfSerialisationHint, TripleFragmentBase
from .datastructuredefinition import QbDataStructureDefinition
from csvqb.models.cube.qb.catalog import CatalogMetadata
from csvqb.utils.uri import uri_safe
from csvqb.utils.validators.uri import validate_uri
from csvqb.utils.validators.file import validate_file_exists
from csvqb.inputs import PandasDataTypes, pandas_input_to_columnar_str
from csvqb.models.validationerror import ValidationError


@dataclass
class QbCodeList(QbDataStructureDefinition, ABC):
    pass


@dataclass
class ExistingQbCodeList(QbCodeList):
    """
    Contains metadata necessary to link a dimension to an existing skos:ConceptScheme.
    """

    concept_scheme_uri: str

    _concept_scheme_uri_validator = validate_uri("concept_scheme_uri")


@dataclass(eq=False, unsafe_hash=False)
class NewQbConcept(UriIdentifiable):

    label: str
    code: str = field(default="")
    parent_code: Optional[str] = field(default=None, repr=False)
    sort_order: Optional[int] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    uri_safe_identifier_override: Optional[str] = field(default=None, repr=False)

    def get_identifier(self) -> str:
        return self.code

    def __post_init__(self):
        if self.code.strip() == "":
            self.code = uri_safe(self.label)

    def __eq__(self, other):
        return isinstance(other, NewQbConcept) and self.code == other.code

    def __hash__(self):
        return self.code.__hash__()


@dataclass
class NewQbCodeListInCsvW(QbCodeList):
    """
    Contains the reference to an existing skos:ConceptScheme defined in a CSV-W.
    """

    schema_metadata_file_path: Path
    csv_file_relative_path_or_uri: str = field(init=False, repr=False)
    concept_scheme_uri: str = field(init=False, repr=False)
    concept_template_uri: str = field(init=False, repr=False)

    _schema_metadata_file_path_validator = validate_file_exists(
        "schema_metadata_file_path"
    )

    @root_validator(pre=True)
    def _csvw_contains_sufficient_information_validator(cls, values: dict) -> dict:
        csv_path = values.get("csv_file_relative_path_or_uri")
        cs_uri = values.get("concept_scheme_uri")
        c_template_uri = values.get("concept_template_uri")
        if csv_path is None or cs_uri is None or c_template_uri is None:
            schema_metadata_file_path = values["schema_metadata_file_path"]
            # The below should throw an exception if there is any problem with the CSV-W.
            extract_code_list_concept_scheme_info(schema_metadata_file_path)

            # if there's no exception but the values aren't set, something weird has happened.
            raise ValueError(
                f"'csv_file_relative_path_or_uri', 'concept_scheme_uri' or 'concept_template_uri' values are missing, "
                f"however the CSV-W seems to contain the relevant information."
            )
        return values

    def __post_init__(self):
        try:
            (
                csv_url,
                cs_uri,
                concept_template_uri,
            ) = extract_code_list_concept_scheme_info(self.schema_metadata_file_path)
            self.csv_file_relative_path_or_uri = csv_url
            self.concept_scheme_uri = cs_uri
            self.concept_template_uri = concept_template_uri
        except Exception:
            # Validation errors will be highlighted later in custom validation function.
            self.csv_file_relative_path_or_uri = None  # type: ignore
            self.concept_scheme_uri = None  # type: ignore
            self.concept_template_uri = None  # type: ignore


@dataclass
class NewQbCodeList(QbCodeList, ArbitraryRdf):
    """
    Contains the metadata necessary to create a new skos:ConceptScheme which is local to a dataset.
    """

    metadata: CatalogMetadata
    concepts: List[NewQbConcept]
    variant_of_uris: List[str] = field(default_factory=list)
    arbitrary_rdf: List[TripleFragmentBase] = field(default_factory=list, repr=False)

    @staticmethod
    def from_data(
        metadata: CatalogMetadata,
        data: PandasDataTypes,
        variant_of_uris: List[str] = [],
    ) -> "NewQbCodeList":
        columnar_data = pandas_input_to_columnar_str(data)
        concepts = [NewQbConcept(c) for c in sorted(set(columnar_data))]
        return NewQbCodeList(metadata, concepts, variant_of_uris=variant_of_uris)

    def get_permitted_rdf_fragment_hints(self) -> Set[RdfSerialisationHint]:
        return {
            RdfSerialisationHint.CatalogDataset,
            RdfSerialisationHint.ConceptScheme,
        }

    def get_default_node_serialisation_hint(self) -> RdfSerialisationHint:
        return RdfSerialisationHint.ConceptScheme

    def validate_data(self, data: PandasDataTypes) -> List[ValidationError]:
        return []  # TODO: implement this.
