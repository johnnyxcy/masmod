import sympy
import typing

__all__ = ["exp", "log"]

exp = typing.cast(typing.Callable[[sympy.Basic], sympy.Expr], sympy.exp)
log = typing.cast(typing.Callable[[sympy.Basic], sympy.Expr], sympy.log)
