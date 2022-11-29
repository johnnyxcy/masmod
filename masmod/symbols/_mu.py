from __future__ import annotations
import sympy
import typing
import varname

from masmod.symbols._theta import Theta
from masmod.symbols._omega import Eta
from masmod.utils.nanoid import generate_nanoid


class Phi(sympy.Symbol):
    __slots__ = ("_mean", "_variance")

    def __new__(cls, name: str, mean: Mu, variance: Eta) -> Phi:
        self = typing.cast(Phi, super().__new__(cls, name))
        self._mean = mean
        self._variance = variance
        return self

    @property
    def mean(self) -> Mu:
        return self._mean

    @property
    def variance(self) -> Eta:
        return self._variance


class Mu:

    def __init__(self, expr: sympy.Expr) -> None:
        for symbol in expr.free_symbols:
            if not isinstance(symbol, Theta):
                raise TypeError("mu 必须关于 Theta 的表达式, {0} 不是 Theta".format(str(symbol)))
            symbol.mu_ref = True

        self.expr = expr

    def __add__(self, other: typing.Any) -> Phi:
        name = varname.varname(raise_exc=False)
        if name is None:
            name = f"PHI_{generate_nanoid()}"
        elif not isinstance(name, str):
            raise ValueError("不合法的 Phi varname")

        if not isinstance(other, Eta):
            raise TypeError("Mu 只支持与 Eta 相加，不支持 {0}".format(str(other)))

        return Phi(name=name, mean=self, variance=other)

    def __repr__(self) -> str:
        return self.expr.__repr__()

    def __str__(self) -> str:
        return self.expr.__str__()