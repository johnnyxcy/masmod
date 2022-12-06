# _*_ coding: utf-8 _*_
"""
File: masmod/masmod/functional/__init__.py

Author: Chongyi Xu <johnny.xcy1997@outlook.com>

File Created: 11/25/2022 05:06 pm

Last Modified: 12/06/2022 04:14 pm

Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>

Copyright (c) 2022 MaS Dev Team
"""
import sympy
import typing

__all__ = ["exp", "log"]

exp = typing.cast(typing.Callable[[sympy.Basic], sympy.Expr], sympy.exp)
log = typing.cast(typing.Callable[[sympy.Basic], sympy.Expr], sympy.log)
