import datetime
from dataclasses import dataclass, field
from typing import List, Set, Dict, TypeVar, Generic, Union, Optional

import pytest

from csvcubedmodels.dataclassbase import DataClassBase


def test_write_to_deep_dict():
    """
    Test conversion of a dataclass structure to dict
    """

    @dataclass
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: A
        b_3: dict

    a = A("Hello from a")
    b = B("Hello from b", a, {"key": "value"})

    b_dict = b.as_dict()

    assert b_dict == {
        "b_1": "Hello from b",
        "b_2": {"a_1": "Hello from a"},
        "b_3": {"key": "value"},
    }


def test_inflate_non_init_fields():
    @dataclass
    class A(DataClassBase):
        a_1: str
        a_2: str = field(init=False)

        def __post_init__(self):
            self.a_2 = self.a_1.capitalize()

    a = A.from_dict({"a_1": "Hello from a", "a_2": "Something different"})

    assert isinstance(a, A)
    assert a.a_1 == "Hello from a"
    assert a.a_2 == "Something different"


def test_inflate_from_deep_dict():
    """
    Test conversion of a deep dictionary to the expected dataclass structure
    """

    @dataclass
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: A
        b_3: dict

    b = B.from_dict(
        {"b_1": "Hello from B", "b_2": {"a_1": "Hello from A"}, "b_3": {"key": "value"}}
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, A)
    assert b.b_2.a_1 == "Hello from A"
    assert isinstance(b.b_3, dict)
    assert b.b_3 == {"key": "value"}


def test_inflate_from_list():
    """
    Test conversion of a deep dictionary to the expected dataclass structure
    """

    @dataclass
    class A(DataClassBase):
        a_1: str
        a_2: List[str]

    a = A.from_dict({"a_1": "Hello from A", "a_2": ["Val 1", "Val 2"]})

    assert isinstance(a, A)
    assert a.a_1 == "Hello from A"
    assert isinstance(a.a_2, list)
    assert a.a_2 == ["Val 1", "Val 2"]


def test_inflate_from_list_deep():
    """
    Test conversion of a deep dictionary inside a generic list to the expected dataclass structure
    """

    @dataclass
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: List[A]

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": [
                {"a_1": "Hello from the first A"},
                {"a_1": "Hello from the second A"},
            ],
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, list)
    assert b.b_2 == [A("Hello from the first A"), A("Hello from the second A")]


def test_inflate_from_set_deep():
    """
    Test conversion of a deep dictionary/set structure to the expected dataclass structure
    """

    @dataclass(unsafe_hash=True)
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: Set[A]

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": [  # Has to be a list since dictionaries are un-hashable (so cannot be in a set).
                {"a_1": "Hello from the first A"},
                {"a_1": "Hello from the second A"},
            ],
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, set)
    assert b.b_2 == {A("Hello from the first A"), A("Hello from the second A")}


def test_inflate_from_deep_generic_type_failure():
    """
    Demonstrate that deserialising more generic types which are have subclasses of DataClassBase as type
     arguments should not succeed.
    """
    T = TypeVar("T")

    @dataclass(unsafe_hash=True)
    class A(DataClassBase, Generic[T]):
        a_1: str

    @dataclass
    class B(DataClassBase, Generic[T]):
        b_1: A[T]

    with pytest.raises(ValueError) as err:
        B[str].from_dict(
            {
                "b_1": {"a_1": "Hello, world"},
            }
        )

    assert "Unable to inflate" in str(err)


def test_inflate_from_dict_deep_failure():
    """
    Demonstrate that deserialising more complex generic types like Dict[str, A] is not currently supported.
    """

    T = TypeVar("T")

    @dataclass
    class A(DataClassBase, Generic[T]):
        a_1: T

    @dataclass
    class B(DataClassBase, Generic[T]):
        b_2: Dict[str, A]

    with pytest.raises(ValueError) as err:
        B.from_dict(
            {
                "b_1": "Hello from B",
                "b_2": {
                    "First": {"a_1": "Hello from the first A"},
                    "Second": {"a_1": "Hello from the second A"},
                },
            }
        )

    assert "Unable to inflate" in str(err)


def test_inflate_from_union_deep():
    """
    Test conversion of a deep Union structure to the expected dataclass structure
    """

    @dataclass(unsafe_hash=True)
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: Union[A, str, List[A]]

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": "Hello again from B",
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, str)
    assert b.b_2 == "Hello again from B"

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": {"a_1": "Hello from A"},
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, A)
    assert b.b_2.a_1 == "Hello from A"

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": [
                {"a_1": "Hello from the first A"},
                {"a_1": "Hello from the second A"},
            ],
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, list)
    assert b.b_2 == [A("Hello from the first A"), A("Hello from the second A")]


def test_inflate_from_list_of_lists_deep():
    """
    Test conversion of a deep list of lists structure to the expected dataclass structure
    """

    @dataclass(unsafe_hash=True)
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: List[List[A]]

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": [[{"a_1": "Hello from A"}]],
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, list)
    assert len(b.b_2) == 1
    first_item = b.b_2[0]
    assert isinstance(first_item, list)
    first_item = first_item[0]
    assert isinstance(first_item, A)
    assert first_item.a_1 == "Hello from A"


def test_inflate_from_list_of_sets_deep():
    """
    Test conversion of a deep list of sets structure to the expected dataclass structure
    """

    @dataclass(unsafe_hash=True)
    class A(DataClassBase):
        a_1: str

    @dataclass
    class B(DataClassBase):
        b_1: str
        b_2: List[Set[A]]

    b = B.from_dict(
        {
            "b_1": "Hello from B",
            "b_2": [[{"a_1": "Hello from A"}]],
        }
    )

    assert isinstance(b, B)
    assert b.b_1 == "Hello from B"
    assert isinstance(b.b_2, list)
    assert len(b.b_2) == 1
    first_item = b.b_2[0]
    assert isinstance(first_item, set)
    first_item = first_item.pop()
    assert isinstance(first_item, A)
    assert first_item.a_1 == "Hello from A"


def test_datetime_json_serialisation():
    @dataclass
    class A(DataClassBase):
        some_datetime: datetime.datetime

    dt = datetime.datetime.now()

    a = A(dt)
    reinflated_a = a.from_json(a.as_json())
    assert isinstance(reinflated_a, A)
    assert reinflated_a.some_datetime == dt


def test_datetime_deserialisation():
    """
    the built in datetime lib doesn't fully support ISO-8601 strings, e.g. "2020-01-01T03:50Z" fails to parse.
     Ensure we're able to parse this example.
    """
    with pytest.raises(ValueError) as err:
        datetime.datetime.fromisoformat("2020-01-01T03:50Z")
        assert err is not None

    @dataclass
    class A(DataClassBase):
        some_datetime: datetime.datetime

    a = A.from_json('{"some_datetime": "2020-01-01T03:50Z"}')
    assert isinstance(a.some_datetime, datetime.datetime)
    assert a.some_datetime == datetime.datetime(2020, 1, 1, 3, 50, tzinfo=datetime.timezone.utc)


def test_date_deserialisation():
    """Ensure we're able to parse dates to the expected type."""
    @dataclass
    class A(DataClassBase):
        some_date: datetime.date

    a = A.from_json('{"some_date": "2020-01-01T03:50Z"}')
    assert isinstance(a.some_date, datetime.date)
    assert not isinstance(a.some_date, datetime.datetime)
    assert a.some_date == datetime.date(2020, 1, 1)


def test_date_json_serialisation():
    @dataclass
    class A(DataClassBase):
        some_datetime: datetime.date

    date = datetime.date.today()

    a = A(date)
    reinflated_a = a.from_json(a.as_json())
    assert isinstance(reinflated_a, A)
    assert reinflated_a.some_datetime == date


def test_override_values():
    @dataclass
    class A(DataClassBase):
        some_optional_value: Optional[str] = None

    a = A("Hello, World")
    a_override = A()

    a.override_with(a_override)

    assert a.some_optional_value is None


def test_overriding_nothing():
    @dataclass
    class A(DataClassBase):
        some_optional_value: Optional[str] = None

    a = A("Hello, World")
    a_override = A()

    a.override_with(a_override, overriding_keys=set())

    assert a.some_optional_value == "Hello, World"


def test_overriding_specific_property():
    @dataclass
    class A(DataClassBase):
        some_value: str
        some_optional_value: Optional[str] = None

    a = A("Hello, world", "This is optional")
    a_override = A("Hello, overriding world.")

    a.override_with(a_override, overriding_keys={"some_value"})

    assert a.some_value == "Hello, overriding world."

    # But some_optional_value doesn't get overridden since it isn't in `overriding_keys`.
    assert a.some_optional_value == "This is optional"


def test_serialise_class_type():
    @dataclass
    class A(DataClassBase):
        some_value: type

    a = A(str)
    a_json_dict = a.as_json_dict()

    assert a_json_dict["some_value"] == "str"

    assert a.as_json() is not None


if __name__ == "__main__":
    pytest.main()
