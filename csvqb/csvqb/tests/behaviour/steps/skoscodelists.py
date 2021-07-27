from behave import Given, When


from csvqb.models.cube import *
from csvqb.writers.skoscodelistwriter import SkosCodeListWriter
from devtools.behave.file import get_context_temp_dir_path


@Given('a NewQbCodeList named "{code_list_name}"')
def step_impl(context, code_list_name: str):
    metadata = CatalogMetadata(
        code_list_name,
        summary="Summary",
        description="Description",
        creator_uri="https://www.gov.uk/government/organisations/office-for-national-statistics",
        publisher_uri="https://www.gov.uk/government/organisations/office-for-national-statistics",
        theme_uris=["http://gss-data.org.uk/def/gdp#some-test-theme"],
        keywords=["Key word one", "Key word two"],
        landing_page_uri="http://example.org/landing-page",
        license_uri="http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        public_contact_point_uri="mailto:something@example.org",
    )

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


@When("the code list is serialised to CSV-W")
def step_impl(context):
    writer = SkosCodeListWriter(context.code_list)
    temp_dir = get_context_temp_dir_path(context)
    writer.write(temp_dir)
