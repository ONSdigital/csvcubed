import pandas as pd
from behave import Given, When


from csvqb.models.cube import *
from csvqb.writers.qbwriter import QbWriter
from devtools.behave.file import get_context_temp_dir_path


def get_standard_catalog_metadata_for_name(name: str) -> CatalogMetadata:
    return CatalogMetadata(
        name,
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


_standard_data = pd.DataFrame(
    {"A": ["a", "b", "c"], "D": ["e", "f", "g"], "Value": [1, 2, 3]}
)


@Given('a single-measure QbCube named "{cube_name}"')
def step_impl(context, cube_name: str):
    columns = [
        QbColumn("A", NewQbDimension.from_data("A code list", _standard_data["A"])),
        QbColumn("D", NewQbDimension.from_data("D code list", _standard_data["D"])),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), _standard_data, columns
    )


@Given('a single-measure QbCube named "{cube_name}" with existing dimensions')
def step_impl(context, cube_name: str):
    columns = [
        QbColumn(
            "A",
            ExistingQbDimension("http://example.org/some/dimension/a"),
            output_uri_template="http://example.org/some/codelist/a",
        ),
        QbColumn(
            "D",
            ExistingQbDimension("http://example.org/some/dimension/d"),
            output_uri_template="http://example.org/some/codelist/d",
        ),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), _standard_data, columns
    )


@Given('a single-measure QbCube named "{cube_name}" with duplicate rows')
def step_impl(context, cube_name: str):
    data = pd.DataFrame({"A": ["a", "a"], "Value": [1, 1]})
    columns = [
        QbColumn("A", NewQbDimension.from_data("A Dimension", data["A"])),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), data, columns
    )


@Given(
    'a single-measure QbCube named "{cube_name}" with codes not defined in the code-list'
)
def step_impl(context, cube_name: str):
    columns = [
        QbColumn(
            "A",
            NewQbDimension(
                "A code list",
                code_list=NewQbCodeList(
                    get_standard_catalog_metadata_for_name("A code list"),
                    [NewQbConcept("a"), NewQbConcept("b")],  # Deliberately missing "c"
                ),
            ),
        ),
        QbColumn("D", NewQbDimension.from_data("D code list", _standard_data["D"])),
        QbColumn(
            "Value",
            QbSingleMeasureObservationValue(
                NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
            ),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), _standard_data, columns
    )


@Given('a multi-measure QbCube named "{cube_name}"')
def step_impl(context, cube_name: str):
    data = pd.DataFrame(
        {
            "A": ["a_height", "a_length"],
            "Measure": ["height", "length"],
            "Value": [1, 20],
        }
    )
    columns = [
        QbColumn("A", NewQbDimension.from_data("A Dimension", data["A"])),
        QbColumn(
            "Measure", QbMultiMeasureDimension.new_measures_from_data(data["Measure"])
        ),
        QbColumn(
            "Value",
            QbMultiMeasureObservationValue(unit=NewQbUnit("meters")),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), data, columns
    )


@Given('a multi-measure QbCube named "{cube_name}" with duplicate rows')
def step_impl(context, cube_name: str):
    data = pd.DataFrame(
        {
            "A": ["a_height", "a_height", "a_length"],
            "Measure": ["height", "height", "length"],
            "Value": [1, 1, 20],
        }
    )
    columns = [
        QbColumn("A", NewQbDimension.from_data("A Dimension", data["A"])),
        QbColumn(
            "Measure", QbMultiMeasureDimension.new_measures_from_data(data["Measure"])
        ),
        QbColumn(
            "Value",
            QbMultiMeasureObservationValue(unit=NewQbUnit("meters")),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), data, columns
    )


@When("the cube is serialised to CSV-W")
def step_impl(context):
    writer = QbWriter(context.cube)
    temp_dir = get_context_temp_dir_path(context)
    writer.write(temp_dir)
