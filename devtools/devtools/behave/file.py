from pathlib import Path
from behave import *


@then('the file at "{file}" should not exist')
def step_impl(context, file):
    assert not Path(file).exists()


@then('the file at "{file}" should exist')
def step_impl(context, file):
    assert Path(file).exists()