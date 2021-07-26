import pandas as pd
from behave import Given, When


from csvqb.models.cube import *
from csvqb.writers.qbwriter import QbWriter
from devtools.behave.file import get_context_temp_dir_path


@Given('a single-measure QbCube named "{cube_name}"')
def step_impl(context, cube_name: str):
    metadata = CatalogMetadata(
        cube_name,
        summary="Summary",
        description="Description",
        creator_uri="https://www.gov.uk/government/organisations/office-for-national-statistics",
        publisher_uri="https://www.gov.uk/government/organisations/office-for-national-statistics",
        theme_uris=["http://gss-data.org.uk/def/gdp#some-test-theme"],
        keywords=["Key word one", "Key word two"],
        landing_page_uri="http://example.org/landing-page",
        license_uri="http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        public_contact_point_uri="something@example.org",
    )

    data = pd.DataFrame(
        {"A": ["a", "b", "c"], "D": ["e", "f", "g"], "Value": [1, 2, 3]}
    )

    columns = [
        QbColumn("A", NewQbDimension.from_data("A code list", data["A"])),
        QbColumn("D", NewQbDimension.from_data("D code list", data["D"])),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    context.cube = Cube(metadata, data, columns)


@When("the cube is serialised to CSV-W")
def step_impl(context):
    writer = QbWriter(context.cube)
    temp_dir = get_context_temp_dir_path(context)
    writer.write(temp_dir)
