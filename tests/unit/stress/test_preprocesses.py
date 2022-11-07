from tempfile import TemporaryDirectory
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
from csvcubed.models.cube.qb.components.measure import ExistingQbMeasure

from tests.stress.buildpreprocess import generate_maximally_complex_csv


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

        numb_rows = 100

        generate_maximally_complex_csv(numb_rows, tmp_dir)

        existing_df = pd.read_csv("tests/test-cases/stress/stress.csv")

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
