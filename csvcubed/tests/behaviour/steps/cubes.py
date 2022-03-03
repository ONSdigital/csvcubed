import ast
from pathlib import Path
from behave import *
from csvcubed.cli.build import build as cli_build
from csvcubeddevtools.helpers.file import get_test_cases_dir


@given('The existing tidy data csv file "{data_file}"')
def step_impl(context, data_file):
    test_case_dir = get_test_cases_dir()
    data_file = Path(test_case_dir, 'config', data_file)
    if not data_file.exists():
        raise Exception(f"Could not find test-case file {data_file}")
    context.data_file = data_file


@given(
    'The config json file "{config_file}" and the existing tidy data csv file '
    '"{data_file}"'
    )
def step_impl(context, config_file, data_file):
    test_case_dir = get_test_cases_dir()
    config_file = Path(test_case_dir, 'config', config_file)
    if not config_file.exists():
        raise Exception(f"Could not find test-case file {config_file}")

    data_file = Path(test_case_dir, 'config', data_file)
    if not data_file.exists():
        raise Exception(f"Could not find test-case file {data_file}")

    context.config_file = config_file
    context.data_file = data_file


@when("The cube is created")
def step_impl(context):
    config_file = context.config_file if hasattr(context, 'config_file') else None
    data_file = context.data_file
    cube, errors = cli_build(data_file, config_file)
    context.cube = cube
    context.errors = errors


@then('The cube Metadata should match')
def step_impl(context):
    expected_meta = eval(context.text.strip().replace('\r\n', ''))
    # expected_meta = ast.literal_eval(context.text.strip().replace('\r\n', ''))
    assert expected_meta == context.cube.metadata.as_json_dict()


@then("The cube Columns should match")
def step_impl(context):
    expected_columns = eval(context.text.strip())
    result = [col.as_json_dict() for col in context.cube.columns]
    for i, col in enumerate(expected_columns):
        assert expected_columns[i] == result[i]
