from pathlib import Path
from shutil import copy
from tempfile import TemporaryDirectory

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from tests.stress.buildpreprocess import generate_maximally_complex_csv
from tests.unit.test_baseunit import get_test_cases_dir

_stress_test_cases_dir = get_test_cases_dir() / "stress"


def test_generated_csv_exists():
    """
    This function checks that `_generate_maximally_complex_csv` generates a csv file and check that the files exist at the desired location
    """
    with TemporaryDirectory() as tmp:

        tmp_dir = Path(tmp)

        numb_rows = 100

        generate_maximally_complex_csv(numb_rows, tmp_dir)

        assert (tmp_dir / "stress.csv").exists()


def test_generated_csv_shape_and_num_unique_values():
    """
    This funcion will check for number of columns and does each column contain the correct amount of unique values
    """
    with TemporaryDirectory() as tmp:

        tmp_dir = Path(tmp)

        copy(
            _stress_test_cases_dir / "existing_stress.csv",
            tmp_dir,
        )

        numb_rows = 100

        generate_maximally_complex_csv(numb_rows, tmp_dir)

        existing_df = pd.read_csv(tmp_dir / "existing_stress.csv")

        generated_df = pd.read_csv(tmp_dir / "stress.csv")

        for c in generated_df.columns:
            assert (
                len(generated_df[c]) == numb_rows
            ), f"{c} does not have {numb_rows} values"
            if c == "Measure":
                assert len(generated_df[c].unique()) == 20
            else:
                assert (
                    len(generated_df[c].unique()) == numb_rows
                ), f"{c} doesn't have {numb_rows} unique values"

        assert_frame_equal(existing_df, generated_df)


if __name__ == "__main__":
    pytest.main()
