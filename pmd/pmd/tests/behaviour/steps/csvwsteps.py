from behave import *
from pathlib import Path


from pmd.codelist.datetimecodelistgen import generate_date_time_code_lists_for_csvw_metadata_file
from devtools.helpers.csvwhelpers import delete_csvw


@Given("a CSV-qb \"{file}\"")
def step_impl(context, file: str):
    context.csvw_path = Path(file)
    context.csvqb_path = Path(file)


@When("a date/time code lists is generated from the CSV-qb")
def step_impl(context):
    output_files = generate_date_time_code_lists_for_csvw_metadata_file(context.csvqb_path)

    def cleanup():
        for metadata_file in output_files:
            delete_csvw(metadata_file)

    context.add_cleanup(cleanup)

