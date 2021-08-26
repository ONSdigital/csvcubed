import pandas as pd
from pathlib import Path
from behave import Given, When, Then


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


@Given(
    'a single-measure QbCube named "{cube_name}" with new attribute values and units'
)
def step_impl(context, cube_name: str):
    data = pd.DataFrame(
        {
            "Existing Dimension": ["a", "b", "c"],
            "New Attribute": ["pending", "final", "in-review"],
            "Value": [2, 2, 2],
        }
    )
    columns = [
        QbColumn(
            "Existing Dimension", ExistingQbDimension("http://existing-dimension")
        ),
        QbColumn(
            "New Attribute",
            NewQbAttribute.from_data("New Attribute", data["New Attribute"]),
        ),
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
    'a single-measure QbCube named "{cube_name}" with one new unit extending another new unit'
)
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
                NewQbMeasure("Some Measure"),
                NewQbUnit(
                    "Some Extending Unit",
                    base_unit=NewQbUnit("Some Base Unit"),
                    base_unit_scaling_factor=1000,
                    qudt_quantity_kind_uri="http://some-quantity-kind",
                    si_base_unit_conversion_multiplier=25.123123,
                ),
            ),
        ),
    ]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), _standard_data, columns
    )


@Then('turtle should be written to "{file}"')
def step_impl(context, file: str):
    temp_dir = get_context_temp_dir_path(context)

    with open(Path(temp_dir / file), "w") as ttl_file:
        ttl_file.write(context.turtle)


@When("the cube is serialised to CSV-W")
def step_impl(context):
    writer = QbWriter(context.cube)
    temp_dir = get_context_temp_dir_path(context)
    writer.write(temp_dir)


@Given(
    'a single-measure QbCube named "{cube_name}" with "{type}" "{data_type}" attribute'
)
def step_impl(context, cube_name: str, type: str, data_type: str):
    data = pd.DataFrame(
        {
            "A": ["uss-cerritos", "uss-titan"],
            "Value": [1, 1],
            "Reg": [75567, 80102],
            "Appeared": ["2020-08-06", "2020-10-08"],
            "First_Captain": ["William Riker", "Carol Freeman"],
        }
    )
    dim = QbColumn("A", NewQbDimension.from_data("A Dimension", data["A"]))
    val = QbColumn(
        "Value",
        QbSingleMeasureObservationValue(
            NewQbMeasure("Some Measure"), NewQbUnit("Some Unit")
        ),
    )
    if data_type == "int":
        if type == "new":
            att = QbColumn(
                "Reg",
                NewQbAttributeLiteral(data_type="int", label="Reg"),
            )
        else:
            att = QbColumn(
                "Reg",
                ExistingQbAttributeLiteral(
                    data_type="int", attribute_uri="http://some-uri"
                ),
            )
        sp1 = SuppressedCsvColumn("Appeared")
        sp2 = SuppressedCsvColumn("First_Captain")
        columns = [dim, val, att, sp1, sp2]
    elif data_type == "date":
        sp1 = SuppressedCsvColumn("Reg")
        if type == "new":
            att = QbColumn(
                "Appeared", NewQbAttributeLiteral(data_type="date", label="Appeared")
            )
        else:
            att = QbColumn(
                "Appeared",
                ExistingQbAttributeLiteral(
                    data_type="date", attribute_uri="http://some-uri"
                ),
            )
        sp2 = SuppressedCsvColumn("First_Captain")
        columns = [dim, val, sp1, att, sp2]
    elif data_type == "string":
        sp1 = SuppressedCsvColumn("Reg")
        sp2 = SuppressedCsvColumn("Appeared")
        if type == "new":
            att = QbColumn(
                "First_Captain",
                NewQbAttributeLiteral(data_type="string", label="First Captain"),
            )
        else:
            att = QbColumn(
                "First_Captain",
                ExistingQbAttributeLiteral(
                    data_type="string", attribute_uri="http://some-uri"
                ),
            )
        columns = [dim, val, sp1, sp2, att]

    context.cube = Cube(
        get_standard_catalog_metadata_for_name(cube_name), data, columns
    )
