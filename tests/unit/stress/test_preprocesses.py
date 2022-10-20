from tempfile import TemporaryDirectory
from pathlib import Path

import pandas as pd
import pytest

from tests.stress.buildpreprocess import _generate_maximally_complex_csv


def test_generated_csv_exists():
    """
        This function checks that `_generate_maximally_complex_csv` generates a csv file and check that the files exist at the desired location
    """
    with TemporaryDirectory() as tmp:

        tmp_dir = Path(tmp)

        numb_rows = 100

        _generate_maximally_complex_csv(numb_rows, tmp_dir)


        assert (tmp_dir / "stress.csv").exists()


def test_generated_csv_shape_and_num_unique_values():
    """
    This funcion will check for number of columns and does each column contain the correct amount of unique values
    """
    with TemporaryDirectory() as tmp:

        tmp_dir = Path(tmp)

        numb_rows = 50

        _generate_maximally_complex_csv(numb_rows, tmp_dir)

        df = pd.read_csv(tmp_dir / "stress.csv")

        assert len(df.columns) == 17

        for c in df.columns:
            assert len(df[c]) == numb_rows, f"{c} does not have {numb_rows} values"
            if c == "Measure":
                assert len(df[c].unique()) == 20
            else:
                assert len(df[c].unique()) == numb_rows, f"{c} doesn't have {numb_rows} unique values"
            

if __name__ == "__main__":
    pytest.main()
        

        