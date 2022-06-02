from behave import Given, When


from csvcubed.models.cube import *
from csvcubed.models.cube import NewQbConcept, DuplicatedQbConcept
from csvcubed.writers.skoscodelistwriter import SkosCodeListWriter
from csvcubeddevtools.behaviour.file import get_context_temp_dir_path


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
