import pytest

from csvcubed.utils.iterables import group_by


def test_group_by():
    """
    Ensure that group_by works as you'd expect.
    """
    grouped_animals = group_by(
        ["Elephant", "Eagle", "Wolf", "Ocelot"],
        # Grouped by the first letter
        lambda animal: animal[0],
    )

    assert grouped_animals == {
        "E": ["Elephant", "Eagle"],
        "O": ["Ocelot"],
        "W": ["Wolf"],
    }


def test_group_by_empty():
    """
    Ensure that group_by works when passed an empty list
    """
    assert group_by([], lambda x: x.cheese_it()) == {}


if __name__ == "__main__":
    pytest.main()
