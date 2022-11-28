import sympy
import typing

from ._context import VarContext
from ._theta import theta
from ._omega import omega
from ._sigma import sigma

ExprContext = VarContext[sympy.Expr]
ConstContext = VarContext[int | float | bool | str]
GlobalContext = VarContext[typing.Any]

__all__ = ["theta", "omega", "sigma", "ExprContext", "ConstContext", "GlobalContext"]