import unittest
from pathlib import Path
import pandas as pd


from csvqb.configloaders.infojson import get_cube_from_info_json


CWD = Path(".")
TEST_CASES_DIR = CWD / ".." / ".." / "test-cases" / "configloaders"
INFO_JSON_PATH = TEST_CASES_DIR / "info.json"
DATA_CSV_PATH = TEST_CASES_DIR / "data.csv"


class InfoJsonLoaderTests(unittest.TestCase):
    def test_something(self):
        data = pd.read_csv(DATA_CSV_PATH)
        cube = get_cube_from_info_json(INFO_JSON_PATH, data)
        self.assertTrue(cube is not None)


if __name__ == '__main__':
    unittest.main()
