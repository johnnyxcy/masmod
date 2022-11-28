from __future__ import annotations
import typing
from _collections_abc import dict_items, dict_keys, dict_values

T = typing.TypeVar("T")
T1 = typing.TypeVar("T1")


class VarContext(typing.Generic[T]):

    def __init__(self) -> None:
        super().__init__()
        self._d: typing.Dict[str, T] = {}

    def as_dict(self) -> typing.Dict[str, typing.Any]:
        return self._d

    def keys(self) -> dict_keys[str, T]:
        return self._d.keys()

    def values(self) -> dict_values[str, T]:
        return self._d.values()

    def items(self) -> dict_items[str, T]:
        return self._d.items()

    def __setitem__(self, __name: str, __value: typing.Any) -> None:
        self._d[__name] = __value

    def __setattr__(self, __name: str, __value: typing.Any) -> None:
        if hasattr(self, "__orig_class__") and isinstance(__value, self.__orig_class__.__args__[0]):
            super().__getattribute__("_d")[__name] = __value
        else:
            super().__setattr__(__name, __value)

    def __getattribute__(self, __name: str) -> typing.Any:
        if __name in super().__getattribute__("_d").keys():
            return super().__getattribute__("_d")[__name]
        return super().__getattribute__(__name)

    def __add__(self, o: VarContext[T1]) -> VarContext[T | T1]:
        _d: typing.Dict[str, typing.Any] = self._d.copy()
        _d.update(o._d.copy())
        context = VarContext[T | T1]()
        context._d = _d
        return context