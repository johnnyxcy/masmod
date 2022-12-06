# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/symbols/_variable.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/28/2022 08:58 pm
#
# Last Modified: 12/06/2022 04:31 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

from __future__ import annotations
import numpy as np
import sympy
import typing

from ._typings import ValueType, BoundsType


class SymVar(sympy.Symbol):
    """包装 sympy.Symbol"""
    __slots__ = ("_init_value", "_bounds", "_fixed")

    def __new__(
        cls,
        name: str,
        init_value: ValueType | None = None,
        bounds: BoundsType | None = None,
        fixed: bool = False
    ) -> SymVar:
        """初始化一个 Variable 对象

        Args:
            name (str): 变量名
            init_value (float | None, optional): 变量的初值，默认为 0
            bounds (Tuple[float | None, float | None] | None, optional): 变量的上下限，默认为 (-inf, inf)
            fixed (bool): 变量的值是否固定，默认为 False

        Returns:
            VarSymbol: 变量对象
        """
        instance = typing.cast(SymVar, super().__new__(cls, name))
        instance.init_value = init_value
        instance.bounds = bounds
        instance._fixed = fixed  # readonly
        return instance

    @property
    def label(self) -> str:
        """参数的名称
        """
        return str(self)

    @property
    def init_value(self) -> float:
        """参数的初值"""
        return self._init_value

    @init_value.setter
    def init_value(self, init_value: ValueType | None) -> None:
        if init_value is None:
            init_value = 0.
        self._init_value = float(init_value)

    @property
    def bounds(self) -> tuple[float, float]:
        """参数的上下限"""
        return self._bounds

    @bounds.setter
    def bounds(self, bounds: BoundsType | None = None) -> None:
        if bounds is not None:
            _lower, _upper = bounds

            if _lower is not None and type(_lower) not in [float, int]:
                raise TypeError("指定的 lower_bound 数据类型错误，必须是 float 或者 int，传入了 {0}".format(type(_lower)))
            elif _lower is None:
                _lower = -np.inf
            else:
                _lower = float(_lower)

            if _upper is not None and not type(_upper) in [float, int]:
                raise TypeError("指定的 upper_bound 数据类型错误，必须是 float 或者 int，传入了 {0}".format(type(_upper)))
            elif _upper is None:
                _upper = np.inf
            else:
                _upper = float(_upper)

            bounds = (_lower, _upper)

        else:
            bounds = (-np.inf, np.inf)

        self._bounds = bounds

    @property
    def fixed(self) -> bool:
        """参数是否固定"""
        return self._fixed