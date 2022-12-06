# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/symbols/_covariate.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/30/2022 03:15 pm
#
# Last Modified: 12/06/2022 04:31 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

from __future__ import annotations

import typing
import sympy
import pandas as pd
from varname import varname


class Covariate(sympy.Symbol):
    __slots__ = ("_series")

    def __new__(cls, name: str, series: pd.Series) -> Covariate:
        """初始化一个 Covariate 对象

        Args:
            name (str): 变量名
            col_name (str) 数据的列名
       
        Returns:
            Covariate: 变量对象
        """
        instance = typing.cast(Covariate, super().__new__(cls, name))
        instance._series = series
        return instance

    @property
    def series(self) -> pd.Series:
        return self._series


def covariate(series: pd.Series) -> Covariate:
    name = varname()

    if not isinstance(name, str):
        raise TypeError("covariate 的变量只能是一个")

    if not isinstance(series, pd.Series):
        raise TypeError("covariate 只支持 pandas.Series 类型")

    return Covariate(name=name, series=series)