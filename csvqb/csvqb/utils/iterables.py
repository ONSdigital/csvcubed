from typing import Iterable, Callable, TypeVar, Optional

T = TypeVar("T")


def first(xs: Iterable[T], predicate: Callable[[T], bool]) -> Optional[T]:
    return next(filter(predicate, xs), None)
