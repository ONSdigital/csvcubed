"""
Lazy Func Descriptor
--------------------

Contains the LazyFuncFieldDescriptor class and function
"""
from dataclasses import field
from typing import Any, Callable, Generic, Mapping, Optional, Type, TypeVar

TClass = TypeVar("TClass")
TRet = TypeVar("TRet")


class LazyFuncFieldDescriptor(Generic[TClass, TRet]):
    """
    A class of Descriptor-typed fields to be used in the lazy_func_field function.

    https://docs.python.org/3/library/dataclasses.html#descriptor-typed-fields
    """

    def __init__(self, gen: Callable[[TClass], TRet]):
        self._gen = gen

    def __set_name__(self, owner, name):
        ...

    def __get__(self, instance: Optional[TClass], t: Type) -> TRet:
        if instance is None:
            # Tell the data class that there is no default value.
            raise AttributeError()

        return self._gen(instance)

    def __set__(self, instance: Any, value: Any) -> None:
        raise NotImplementedError()


def lazy_func_field(
    value_generator: Callable[[TClass], TRet],
    repr: bool = True,
    hash: Optional[bool] = None,
    compare: bool = False,
    metadata: Optional[Mapping] = None,
) -> TRet:
    """
    Allows you to define a dataclass field which returns the value of a function evaluated (lazily) upon accessing the
    attribute.

    These fields are read-only.

    We lie a bit about the return type so that pyright will be happy type checking our functions.
    """
    return field(
        init=False,
        default=LazyFuncFieldDescriptor(value_generator),
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=metadata,
    )  # type: ignore
