from behave import Given, When

from csvcubedpmd.codelistcli.datetimecodelistgen import (
    generate_date_time_code_lists_for_csvw_metadata_file,
)
from csvcubeddevtools.behaviour.file import get_context_temp_dir_path


@Given('a CSV-qb "{file}"')
def step_impl(context, file: str):
    temp_dir = get_context_temp_dir_path(context)
    context.csvw_path = temp_dir / file
    context.csvqb_path = temp_dir / file


@When("a date/time code lists is generated from the CSV-qb")
def step_impl(context):
    temp_dir = get_context_temp_dir_path(context)
    generate_date_time_code_lists_for_csvw_metadata_file(
        context.csvqb_path.absolute(), output_directory=temp_dir
    )
