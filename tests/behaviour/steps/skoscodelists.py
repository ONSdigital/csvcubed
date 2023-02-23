import shutil
from pathlib import Path

from behave import Given, When, then
from csvcubeddevtools.behaviour.file import get_context_temp_dir_path
from csvcubeddevtools.helpers.file import get_test_cases_dir

from csvcubed.cli.build_code_list import build_code_list as _build_code_list
from csvcubed.models.cube.qb.catalog import CatalogMetadata
from csvcubed.models.cube.qb.components.codelist import (
    CompositeQbCodeList,
    NewQbCodeList,
)
from csvcubed.models.cube.qb.components.concept import DuplicatedQbConcept, NewQbConcept
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter

_test_case_dir = get_test_cases_dir()


def get_standard_catalog_metadata_for_name(name: str) -> CatalogMetadata:
    return CatalogMetadata(
        name,
        summary="Summary",
        description="Description",
        creator_uri="https://www.gov.uk/government/organisations/office-for-national-statistics",
        publisher_uri="https://www.gov.uk/government/organisations/office-for-national-statistics",
        theme_uris=["http://gss-data.org.uk/def/gdp#some-test-theme"],
        keywords=["Key word one", "Key word two"],
        landing_page_uris=["http://example.org/landing-page"],
        license_uri="http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        public_contact_point_uri="mailto:something@example.org",
    )


@Given('a NewQbCodeList named "{code_list_name}"')
def step_impl(context, code_list_name: str):
    metadata = get_standard_catalog_metadata_for_name(code_list_name)

    context.code_list = NewQbCodeList(
        metadata,
        [
            NewQbConcept(
                "First Concept",
                code="1st-concept",
                description="This is the first concept.",
            ),
            NewQbConcept("Second Concept", parent_code="1st-concept", sort_order=20),
        ],
    )


@Given('a CompositeQbCodeList named "{code_list_name}"')
def step_impl(context, code_list_name: str):
    metadata = get_standard_catalog_metadata_for_name(code_list_name)

    context.code_list = CompositeQbCodeList(
        metadata,
        [
            DuplicatedQbConcept(
                existing_concept_uri="http://data.europa.eu/nuts/code/UKL",
                label="Wales",
                code="wales",
            ),
            DuplicatedQbConcept(
                existing_concept_uri="http://data.europa.eu/nuts/code/UKM",
                label="Scotland",
                code="scotland",
            ),
            DuplicatedQbConcept(
                existing_concept_uri="http://statistics.data.gov.uk/id/statistical-geography/E92000001",
                label="England",
                code="england",
            ),
        ],
        variant_of_uris=[
            "http://data.europa.eu/nuts/scheme/2016",
            "http://gss-data.org.uk/def/concept-scheme/geography-hierarchy/administrative",
        ],
    )


@Given('a NewQbCodeList named "{code_list_name}" containing duplicates')
def step_impl(context, code_list_name: str):
    metadata = get_standard_catalog_metadata_for_name(code_list_name)

    context.code_list = NewQbCodeList(
        metadata,
        [
            NewQbConcept(
                "First Concept",
                code="1st-concept",
                description="This is the first concept.",
            ),
            NewQbConcept(
                "Pretend other Concept",
                code="1st-concept",
                description="This is really the first concept again.",
            ),
        ],
    )


@When("the code list is serialised to CSV-W")
def step_impl(context):
    writer = SkosCodeListWriter(context.code_list)
    temp_dir = get_context_temp_dir_path(context)
    writer.write(temp_dir)


@then(
    'a valid code-list is created and serialised to CSVW from the config file "{config_file}"'
)
def step_imp(context, config_file: Path):
    _temp_test_cases_dir = get_context_temp_dir_path(context)

    shutil.copy((_test_case_dir / config_file), _temp_test_cases_dir)

    config_file_path = _temp_test_cases_dir / config_file

    _build_code_list(
        config_path=config_file_path,
        output_directory=_temp_test_cases_dir / "out",
        fail_when_validation_error_occurs=True,
        validation_errors_file_name=None,
    )
