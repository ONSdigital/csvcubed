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
