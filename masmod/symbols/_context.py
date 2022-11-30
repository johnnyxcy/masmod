from __future__ import annotations
import typing
from _collections_abc import dict_items, dict_keys, dict_values

T = typing.TypeVar("T")
P = typing.TypeVar("P")


class VarContext(typing.Generic[T]):

    def __init__(self, d: typing.Dict[str, T] | None = None) -> None:
        super().__init__()
        if not d:
            d = {}
        self._d: typing.Dict[str, T] = d

    @property
    def generic_T(self) -> typing.Type[T]:
        if not hasattr(self, "__orig_class__"):
            raise ValueError("构建 VarContext 必须要提供模版类型，类似于 ctx = VarContext[int | float]()")
        _generic_T, = typing.get_args(self.__orig_class__)
        return _generic_T

    def __repr__(self) -> str:
        return self._d.__repr__()

    def __str__(self) -> str:
        return self._d.__str__()

    def copy(self) -> VarContext[T]:
        _generic_T = self.generic_T
        _d = self._d.copy()
        return VarContext[_generic_T](_d)

    def as_dict(self) -> typing.Dict[str, T]:
        return self._d

    def keys(self) -> dict_keys[str, T]:
        return self._d.keys()

    def values(self) -> dict_values[str, T]:
        return self._d.values()

    def items(self) -> dict_items[str, T]:
        return self._d.items()

    def __setitem__(self, __name: str, __value: typing.Any) -> None:
        # TODO: maybe add type check
        # if self.generic_T != typing.Any and not isinstance(__value, self.generic_T):
        #     raise TypeError("{0} 是 {1} 类型，与给定的 {2} 类型不符".format(__name, type(__value), self.generic_T))
        self._d[__name] = __value

    def __getattribute__(self, __name: str) -> typing.Any:
        if __name in object.__getattribute__(self, "_d").keys():
            return object.__getattribute__(self, "_d")[__name]
        return object.__getattribute__(self, __name)

    def __add__(self, o: VarContext[P]) -> VarContext[T | P]:
        _d: typing.Dict[str, T | P] = {
            **self._d.copy()
        }
        _d.update(o._d.copy())

        _generic_T = self.generic_T

        return VarContext[typing.Union[_generic_T, o.generic_T]](_d)
