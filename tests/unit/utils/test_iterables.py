import pytest

from csvcubed.utils.iterables import group_by, single


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


def test_single_correctly_extracts_single_matching_value():
    """
    Ensures that we can pick out the single value in an iterable matching a predicate.
    """
    even_number = single([1, 2, 3], lambda x: x % 2 == 0)
    assert even_number == 2


def test_single_no_matches_exception():
    """
    Ensures that we raise a KeyError when trying to match on a single item in a list where no item matches the
      predicate.
    """
    with pytest.raises(KeyError) as err:
        single([1, 3], lambda x: x % 2 == 0, "even number")
    assert "Could not find the anticipated even number" in str(err.value)


def test_single_duplicate_matches_exception():
    """
    Ensures that we raise a KeyError when trying to match on a single item in a list where multiple items matches the
      predicate.
    """
    with pytest.raises(KeyError) as err:
        single([1, 2, 3, 4], lambda x: x % 2 == 0)
    assert "Found more than one matching item" in str(err.value)


if __name__ == "__main__":
    pytest.main()
