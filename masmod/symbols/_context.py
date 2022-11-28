from __future__ import annotations
import typing

T = typing.TypeVar("T")
T1 = typing.TypeVar("T1")


class VarContext(typing.Generic[T]):

    def __init__(self) -> None:
        super().__init__()
        self._d: typing.Dict[str, typing.Any] = {}

    def __setitem__(self, __name: str, __value: typing.Any) -> None:
        self._d[__name] = __value

    def __setattr__(self, __name: str, __value: typing.Any) -> None:
        if __name == "_d":
            super().__setattr__("_d", __value)
        else:
            super().__getattribute__("_d")[__name] = __value

    def __getattribute__(self, __name: str) -> typing.Any:
        if __name in super().__getattribute__("_d").keys():
            return super().__getattribute__("_d")[__name]
        return super().__getattribute__(__name)

    def __add__(self, o: VarContext[T1]) -> VarContext[T | T1]:
        _d = self._d.copy()
        _d.update(o._d.copy())
        context = VarContext[T | T1]()
        context._d = _d
        return context