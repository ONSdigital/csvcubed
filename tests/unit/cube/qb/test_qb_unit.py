import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from csvcubed.definitions import APP_ROOT_DIR_PATH
from csvcubed.models.cube.qb.columns import QbColumn
from csvcubed.models.cube.qb.components.observedvalue import QbObservationValue
from csvcubed.models.cube.qb.components.unit import ExistingQbUnit, NewQbUnit
from csvcubed.readers.cubeconfig.v1.columnschema import (
    EXISTING_UNIT_DEFAULT_SCALING_FACTOR,
)
from csvcubed.readers.cubeconfig.v1.configdeserialiser import get_deserialiser
from tests.unit.test_baseunit import assert_num_validation_errors, get_test_cases_dir

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"
SCHEMA_PATH_FILE = APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_0" / "schema.json"


def test_scaling_factor_defined():
    with TemporaryDirectory() as t:
        temp_dir = Path(t)

        cube_config = {
            "columns": {
                "Amount": {
                    "type": "observations",
                    "unit": {
                        "label": "Count",
                        "from_existing": "http://qudt.org/vocab/unit/NUM",
                        "scaling_factor": 0.1,
                    },
                }
            }
        }

        data = pd.DataFrame({"Dimension 1": ["A", "B", "C"], "Amount": [100, 200, 300]})

        data_file_path = temp_dir / "data.csv"
        config_file_path = temp_dir / "config.json"

        with open(config_file_path, "w+") as config_file:
            json.dump(cube_config, config_file, indent=4)

        data.to_csv(str(data_file_path), index=False)

        deserialiser = get_deserialiser(SCHEMA_PATH_FILE, 3)

        cube, _, _ = deserialiser(data_file_path, config_file_path)
        amount_col = cube.columns[1]

        assert_num_validation_errors(amount_col.validate(), 0)

        assert isinstance(amount_col, QbColumn)
        assert isinstance(amount_col.structural_definition, QbObservationValue)
        assert amount_col.structural_definition.measure is None
        unit = amount_col.structural_definition.unit
        assert isinstance(unit, NewQbUnit)
        assert unit.base_unit_scaling_factor == 0.1


def test_scaling_factor_not_defined():
    with TemporaryDirectory() as t:
        temp_dir = Path(t)

        cube_config = {
            "columns": {
                "Amount": {
                    "type": "observations",
                    "unit": {
                        "label": "Count",
                        "from_existing": "http://qudt.org/vocab/unit/NUM",
                    },
                }
            }
        }

        data = pd.DataFrame({"Dimension 1": ["A", "B", "C"], "Amount": [100, 200, 300]})

        data_file_path = temp_dir / "data.csv"
        config_file_path = temp_dir / "config.json"

        with open(config_file_path, "w+") as config_file:
            json.dump(cube_config, config_file, indent=4)

        data.to_csv(str(data_file_path), index=False)

        deserialiser = get_deserialiser(SCHEMA_PATH_FILE, 3)

        cube, _, _ = deserialiser(data_file_path, config_file_path)
        amount_col = cube.columns[1]

        assert_num_validation_errors(amount_col.validate(), 0)

        assert isinstance(amount_col, QbColumn)
        assert isinstance(amount_col.structural_definition, QbObservationValue)
        assert amount_col.structural_definition.measure is None
        unit = amount_col.structural_definition.unit
        assert isinstance(unit, NewQbUnit)
        assert unit.base_unit_scaling_factor == EXISTING_UNIT_DEFAULT_SCALING_FACTOR


def _assert_both_properties_defined_error(
    unit: NewQbUnit, provided_variable_name: str, expected_variable_name: str
) -> None:
    errors = unit.pydantic_validation()
    assert_num_validation_errors(errors, 1)
    error = errors[0]
    assert provided_variable_name in str(error)
    assert expected_variable_name in str(error)


if __name__ == "__main__":
    pytest.main()
