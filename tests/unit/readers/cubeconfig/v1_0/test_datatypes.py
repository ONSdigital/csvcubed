import pandas as pd

from csvcubed.readers.cubeconfig.v1 import datatypes

from .virtualconfigs import VirtualConfigurations as vc
from tests.unit.test_baseunit import get_test_cases_dir
from pathlib import Path
import json

TEST_CASE_DIR = (
    get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0" / "data_typing"
)


def _assert_dict(got: dict, expected: dict):
    """
    Helper for a light touch comparisson between a created dictionary
    and an expected dictionary.
    """

    assert len(got) == len(expected), (
        'Unexpected number of items:\n'
        f'Got: {", ".join(got.keys())}\n'
        f'Expected: {",".join(expected.keys())}'
    )
    for k, v in got.items():
        assert (
            k in expected
        ), f'Unexpected key found: "{k}". The expected keys were: {",".join(expected.keys())}'
        expected_v = expected[k]
        assert (
            v == expected_v
        ), f"For field {k}, expexcted value: {expected_v}, got value {v}"


def test_configured_dimension_dtypes():
    """
    Test that where given a a configured dimension, that dimension is
    mapped to the dimemnsion type of string.
    """

    for config in [
        vc.DIMENSION_CONFIG_POPULATED,
        vc.DIMENSION_EXISTING,
        vc.DIMENSION_EXISTING_CODELIST,
        vc.DIMENSION_WITH_LABEL,
        vc.LABEL_ONLY,
    ]:

        # Assert expected dtype
        dtype = datatypes.pandas_dtypes_from_columns_config({"Dimension": config})
        _assert_dict(dtype, {"Dimension": "string"})


def test_attribute_literal_dtypes():
    """
    Test that where given a literal attribute, the provided datatype is
    mapped to our corresponding pandas datatype.
    """

    # It shouldnt matter which variation of an attribute literal but we'll
    # test with both to be thorough
    for config in [vc.ATTRIBUTE_NEW_LITERAL, vc.ATTRIBUTE_EXISTING_LITERAL]:

        for csvw_type, pandas_type in datatypes.PANDAS_DTYPE_MAPPING.items():

            # Reassign datatype for test
            config["data_type"] = csvw_type

            # Assert expected dtype
            dtype = datatypes.pandas_dtypes_from_columns_config({"Attribute": config})
            _assert_dict(dtype, {"Attribute": pandas_type})


def test_assignable_pandas_datatypes_are_valid():
    """
    Confirm that all pandas dtypes we are mapping to are valid and
    can be used while loading a dataframe.
    """

    pandas_dtypes = set(datatypes.PANDAS_DTYPE_MAPPING.values())

    for pdt in pandas_dtypes:
        df = pd.DataFrame({"column": [1, 2, 3, 4, 5]}, dtype=pdt)
        assert df["column"].dtype == pdt


def test_datatypes_without_convention():
    """
    Confirm expected datatypes when using a fully configured dataset.
    """

    csv_path = Path(TEST_CASE_DIR / "datatypes_simple.csv")
    config_path = Path(TEST_CASE_DIR / "datatypes_simple.json")

    with open(config_path) as f:
        config = json.load(f)

    dtype = datatypes.get_pandas_datatypes(csv_path, config=config)
    _assert_dict(
        dtype,
        {
            "Dim-0": "string",
            "Dim-1": "string",
            "Dim-2": "string",
            "Attr-1": "uint64",
            "Value": "float64",
            "Measure": "string",
            "Units": "string",
        },
    )


def test_datatypes_with_convention():
    """
    Confirm expected datatypes when using a fully configured by convention dataset.
    """

    csv_path = Path(TEST_CASE_DIR / "datatypes_simple.csv")
    dtype = datatypes.get_pandas_datatypes(csv_path)

    _assert_dict(
        dtype,
        {
            "Dim-0": "string",
            "Dim-1": "string",
            "Dim-2": "string",
            "Attr-1": "string",
            "Value": "float64",
            "Measure": "string",
            "Units": "string",
        },
    )


def test_datatypes_with_and_without_convention():
    """
    Confirm expected datatypes when using a mix of from explicit and by
    convention configuration.
    """
    ...
