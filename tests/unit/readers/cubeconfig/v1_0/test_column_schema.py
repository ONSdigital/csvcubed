from csvcubed.models.cube import NewQbUnit, ExistingQbUnit
from csvcubed.readers.cubeconfig.v1.columnschema import (
    EXISTING_UNIT_DEFAULT_SCALING_FACTOR,
    Unit,
    _get_unit_scaling_factor,
)


def test_new_unit():
    """
    Scaling factor of a new unit should be None.
    """
    unit = Unit("New Unit")
    scaling_factor = _get_unit_scaling_factor(unit)

    assert scaling_factor is None


def test_existing_unit_without_scaling_factor():
    """
    Scaling factor of an existing unit should be 1.0 when it is not defined.
    """
    unit = Unit(
        "Unit From Existing Unit", from_existing="http://qudt.org/vocab/unit/NUM"
    )
    scaling_factor = _get_unit_scaling_factor(unit)

    assert scaling_factor == EXISTING_UNIT_DEFAULT_SCALING_FACTOR


def test_existing_unit_with_scaling_factor():
    """
    Scaling factor of an existing unit should be the user-defined scaling factor when it is defined.
    """
    unit = Unit(
        "Unit From Existing Unit",
        from_existing="http://qudt.org/vocab/unit/NUM",
        scaling_factor=0.01,
    )
    scaling_factor = _get_unit_scaling_factor(unit)

    assert scaling_factor == 0.01
