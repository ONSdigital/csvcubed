"""
Iterables
---------

Function to help when working with lists/iterables.
"""
from collections.abc import Iterable
from typing import Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")


def first(
    xs: Iterable[T], predicate: Callable[[T], bool] = lambda a: True
) -> Optional[T]:
    """
    :return: the first item in the :obj:`~collections.abc.Iterable` :obj:`xs` which matches
        the :func:`predicate` function.
    """
    return next(filter(predicate, xs), None)


def single(
    xs: Iterable[T],
    predicate: Callable[[T], bool] = lambda a: True,
    item_name: str = "item",
) -> T:
    """
    :return: the single item in the :obj:`~collections.abc.Iterable` :obj:`xs` which matches
        the :func:`predicate` function. If zero items match the predicate, or more than one
        item matches the predicate then an exception is raised.
    """
    matching_values = [x for x in xs if predicate(x)]

    if not any(matching_values):
        raise KeyError(f"Could not find the anticipated {item_name}.")

    if len(matching_values) > 1:
        raise KeyError(
            f"Found more than one matching {item_name}: {matching_values}. Expected only one."
        )

    return matching_values[0]


def group_by(xs: Iterable[T], get_key: Callable[[T], str]) -> Dict[str, List[T]]:
    """
    Generates a dictionary containing items grouped by each key.
    """
    groups: Dict[str, List[T]] = {}
    for x in xs:
        key = get_key(x)
        if key not in groups:
            groups[key] = []
        groups[key].append(x)

    return groups
