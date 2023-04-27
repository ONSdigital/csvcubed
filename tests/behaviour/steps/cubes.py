import datetime
import json
from contextlib import ExitStack
from typing import List, Optional

import pandas as pd
import vcr
from behave import *
from csvcubeddevtools.behaviour.file import get_context_temp_dir_path
from csvcubeddevtools.helpers.file import get_test_cases_dir
from pandas.testing import assert_frame_equal

from csvcubed.cli.build import build as cli_build
from csvcubed.models.cube.columns import CsvColumn
from csvcubed.utils.cache import session
from tests.helpers.schema_mocking import mock_json_schemas

_test_case_dir = get_test_cases_dir()
_cube_config_test_case_dir = _test_case_dir / "readers" / "cube-config"
_cassettes_dir = _test_case_dir / "vcrpy-cassettes"


@given('the existing tidy data csv file "{data_file}"')
def step_impl(context, data_file):
    data_file = _cube_config_test_case_dir / data_file
    if not data_file.exists():
        raise Exception(f"Could not find test-case file {data_file}")
    context.data_file = data_file


@given(
    'the config json file "{config_file}" and the existing tidy data csv file '
    '"{data_file}"'
)
def step_impl(context, config_file, data_file):
    config_file = _cube_config_test_case_dir / config_file
    if not config_file.exists():
        raise Exception(f"Could not find test-case file {config_file}")

    data_file = _cube_config_test_case_dir / data_file
    if not data_file.exists():
        raise Exception(f"Could not find test-case file {data_file}")

    context.config_file = config_file
    context.data_file = data_file


@when("a valid cube is built and serialised to CSV-W")
def step_impl(context):
    _build_valid_cube(context)


@then("a valid cube can be built and serialised to CSV-W")
def step_impl(context):
    _build_valid_cube(context)


def _build_valid_cube(context):
    config_file = context.config_file if hasattr(context, "config_file") else None
    data_file = context.data_file
    scenario_name = context.scenario.name
    cassette_file_name = (
        scenario_name.rsplit("]")[1] if "]" in scenario_name else scenario_name
    )

    # Disable HTTP cache, don't want to be competing with vcrpy here.
    exit_stack = ExitStack()
    exit_stack.enter_context(session.cache_disabled())
    context.add_cleanup(lambda: exit_stack.pop_all().close())

    context.out_dir = get_context_temp_dir_path(context) / "out"

    with vcr.use_cassette(
        str(_cassettes_dir / f"build-cube-{cassette_file_name}.yaml"),
        record_mode=vcr.record_mode.RecordMode.NEW_EPISODES,  # Changed this temporarily to resolve an issue with inconsistent run order when using vcrpy and mockers together.
    ):
        mocker = mock_json_schemas()
        mocker.start()
        context.add_cleanup(lambda: mocker.stop())

        cube, errors = cli_build(
            data_file,
            config_file,
            output_directory=context.out_dir,
            validation_errors_file_name="validation_errors.json",
        )

        context.cube = cube

        assert not any(errors), [e.message for e in errors]


@then("the cube Metadata should match")
def step_impl(context):
    expected_meta = eval(context.text.strip().replace("\r\n", ""))
    result_dict = context.cube.metadata.as_json_dict()

    if expected_meta != result_dict:
        # Print the mis-matched values if the whole dict is not equal
        for k, v in result_dict.items():
            true_value = result_dict[k]
            if isinstance(true_value, (datetime.datetime, datetime.date)):
                true_value = true_value.isoformat()

            if expected_meta[k] != true_value:
                raise Exception(
                    f"Key: {k} - result: {result_dict[k]} does not match expected: {expected_meta[k]}"
                )
    assert expected_meta == result_dict


@then("the cube columns should match")
def step_impl(context):
    cols: List[CsvColumn] = context.cube.columns
    print("cols:", cols)
    expected_cols: List[str] = json.loads(context.text)
    for col in cols:
        assert col.csv_column_title in expected_cols


@then("the cube data should match")
def step_impl(context):
    data: Optional[pd.DataFrame] = context.cube.data
    print("data:", data)
    expected_data = pd.read_json(context.text, orient="records", dtype=False)
    assert_frame_equal(expected_data, data, check_dtype=False, check_categorical=False)
