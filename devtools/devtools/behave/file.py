from behave import then
from .temporarydirectory import get_context_temp_dir_path


@then('the file at "{file}" should not exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert not (temp_dir / file).exists()


@then('the file at "{file}" should exist')
def step_impl(context, file):
    temp_dir = get_context_temp_dir_path(context)
    assert (temp_dir / file).exists()
