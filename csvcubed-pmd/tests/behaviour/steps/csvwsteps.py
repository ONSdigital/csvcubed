from behave import Given, When

from csvcubeddevtools.behaviour.file import get_context_temp_dir_path


@Given('a CSV-qb "{file}"')
def step_impl(context, file: str):
    temp_dir = get_context_temp_dir_path(context)
    context.csvw_path = temp_dir / file
    context.csvqb_path = temp_dir / file
