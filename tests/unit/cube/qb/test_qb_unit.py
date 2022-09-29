import pytest
from pathlib import Path
import pandas as pd
import json
from tempfile import TemporaryDirectory

from csvcubed.models.cube import NewQbUnit, ExistingQbUnit
from csvcubed.models.cube.qb.components.observedvalue import (
    QbStandardShapeObservationValue,
)
from csvcubed.models.cube.qb import QbColumn
from csvcubed.readers.cubeconfig.v1.columnschema import (
    EXISTING_UNIT_DEFAULT_SCALING_FACTOR,
)
from csvcubed.readers.cubeconfig.v1.configdeserialiser import get_deserialiser
from csvcubed.definitions import APP_ROOT_DIR_PATH
from tests.unit.test_baseunit import assert_num_validation_errors
from tests.unit.test_baseunit import get_test_cases_dir

TEST_CASE_DIR = get_test_cases_dir().absolute() / "readers" / "cube-config" / "v1.0"
SCHEMA_PATH_FILE = APP_ROOT_DIR_PATH / "schema" / "cube-config" / "v1_0" / "schema.json"


def test_new_unit_base_unit_validation():
    """
    Ensure that if :obj:`base_unit_scaling_factor` is specified and :obj:`base_unit` isn't,
    the user gets a suitable validation error.
    """

    _assert_both_properties_defined_error(
        NewQbUnit(
            "Some Unit",
            base_unit=None,
            base_unit_scaling_factor=1000.0,
        ),
        "base_unit_scaling_factor",
        "base_unit",
    )

    # Now check that valid states don't trigger the error.
    assert_num_validation_errors(NewQbUnit("Some Unit").pydantic_validation(), 0)

    assert_num_validation_errors(
        NewQbUnit(
            "Some Unit",
            base_unit=ExistingQbUnit("http://some-existing-unit"),
            base_unit_scaling_factor=1000.0,
        ).pydantic_validation(),
        0,
    )


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

        assert_num_validation_errors(amount_col.pydantic_validation(), 0)

        assert isinstance(amount_col, QbColumn)
        assert isinstance(
            amount_col.structural_definition, QbStandardShapeObservationValue
        )
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

        assert_num_validation_errors(amount_col.pydantic_validation(), 0)

        assert isinstance(amount_col, QbColumn)
        assert isinstance(
            amount_col.structural_definition, QbStandardShapeObservationValue
        )
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
