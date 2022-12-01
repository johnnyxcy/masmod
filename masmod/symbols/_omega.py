from __future__ import annotations

import numpy as np
import typing
from varname import varname, ImproperUseError
from dataclasses import dataclass
from masmod.symbols._variable import SymVar
from masmod.symbols._typings import ValueType, BoundsType


class Eta(SymVar):
    """
    随机效应的变量
    """
    __slots__ = ("_omega")

    @property
    def omega(self) -> Omega:
        """
        Eta 的 Omega 矩阵
        """
        return self._omega

    @omega.setter
    def omega(self, omega: Omega):
        """
        设定 Eta 的 Omega 矩阵

        Args:
            omega: Omega 矩阵
        """

        if not isinstance(omega, Omega):
            raise ValueError(f'指定的 omega 必须是 Omega 的实例, 传入了 {type(omega)}')
        self._omega = omega


@dataclass
class OmegaBlock:
    """通过下三角矩阵构建 Omega

    Examples:
        >>> block = OmegaBlock(
            tril=[
                1,
                0, 1
            ],
            dimension=2
        )
        >>> # [
        >>> #   [1, 0],
        >>> #   [0, 1]
        >>> # ]
    """
    tril: list[ValueType] | np.ndarray  # 下三角矩阵的值 (一维数组)
    dimension: int  # block 的 dimension


class Omega:
    """
    随机效应的矩阵
    """

    def __init__(
        self, names: list[str], init_values: np.ndarray, lower_bounds: np.ndarray, upper_bounds: np.ndarray
    ) -> None:
        self.__names = names
        self.init_values = init_values
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds

    @classmethod
    def from_ndarray(cls, array: np.ndarray) -> Omega:
        names: list[str] = [_eta.name for _eta in np.diag(array)]
        init_values: np.ndarray = np.zeros(array.shape)
        lower_bounds: np.ndarray = np.zeros(array.shape)
        upper_bounds: np.ndarray = np.zeros(array.shape)

        for row in range(array.shape[0]):
            for col in range(array.shape[1]):
                cell = array[row][col]
                if isinstance(cell, Eta):
                    init_values[row][col] = cell.init_value

                    lower_bounds[row][col] = cell.bounds[0]
                    upper_bounds[row][col] = cell.bounds[1]
                else:
                    init_values[row][col] = cell
                    lower_bounds[row][col] = cell
                    upper_bounds[row][col] = cell

        return cls(names=names, init_values=init_values, lower_bounds=lower_bounds, upper_bounds=upper_bounds)

    @property
    def names(self) -> list[str]:
        return self.__names


@typing.overload
def omega(init_omega: ValueType | None = None, bounds: BoundsType | None = None, fixed: bool = False) -> Eta:
    """生成单个 eta 对象

    Args:
        init_omega (ValueType | None, optional): eta 的初值，默认为 1
        bounds (BoundsType | None, optional): eta 的上下限，默认为 (-inf, inf)
        fixed (bool, optional): eta 是否固定，默认为 False

    Returns:
        Eta: 单个 eta 对象
    """
    ...


@typing.overload
def omega(init_omega: OmegaBlock,
            bounds: list[BoundsType | None] | np.ndarray | None = None,
            fixed: bool = False) -> list[Eta]:
    """通过下三角矩阵构建 eta 对象

    Args:
        init_omega (OmegaBlock): 下三角矩阵
        bounds (list[BoundsType] | np.ndarray | None, optional): 每个 eta 的上下限，默认所有的 eta 都为 (-inf, inf)
        fixed (bool, optional): 是否固定，如果为 True 整个下三角矩阵构建的 Omega 都会固定，默认为 False

    Returns:
        list[Eta]: 生成的多个 eta 对象
    """
    ...


@typing.overload
def omega(
    init_omega: list[list[ValueType]] | np.ndarray,
    bounds: list[BoundsType | None] | np.ndarray | None = None,
    fixed: bool = False,
) -> list[Eta]:
    """通过完整 Omega 矩阵构建 eta 对象

    Args:
        init_omega (list[list[ValueType]] | np.ndarray): 完整 Omega 矩阵，必须为方块矩阵
        bounds (list[BoundsType] | np.ndarray | None, optional): 每个 eta 的上下限，默认所有的 eta 都为 (-inf, inf)
        fixed (bool, optional): 是否固定，如果为 True 整个 Omega 都会固定，默认为 False

    Returns:
        list[Eta]: 生成的多个 eta 对象
    """
    ...


def omega(
    init_omega: ValueType | OmegaBlock | np.ndarray | list[list[ValueType]] | None = None,
    bounds: BoundsType | np.ndarray | list[BoundsType | None] | None = None,
    fixed: bool = False
) -> Eta | list[Eta]:
    omega_mat: np.ndarray

    if init_omega is None:
        # 默认 Omega 构建，对角线为 1 的 1x1 Omega 矩阵
        omega_mat = np.array([[1]], dtype=float)
    elif isinstance(init_omega, ValueType):
        # 单一值的 Omega 构建，将 eta 初值放置于 1x1 Omega 的对角线即可
        omega_mat = np.array([[init_omega]], dtype=float)

    elif isinstance(init_omega, OmegaBlock):
        # 使用下三角构建 Omega 矩阵
        tri_lower_indicies = np.tril_indices(init_omega.dimension)
        tri_lower_len = len(tri_lower_indicies[0])
        if len(init_omega.tril) != tri_lower_len:
            raise ValueError(
                "指定的维数 {0} 需要 {1} 个参数，与传入的参数个数 {2} 不符 ".format(
                    init_omega.dimension, tri_lower_len, len(init_omega.tril)
                )
            )
        tmp = np.zeros([init_omega.dimension, init_omega.dimension])
        tmp[tri_lower_indicies] = init_omega.tril
        omega_mat = tmp + tmp.T - np.diag(np.diag(tmp))

    elif isinstance(init_omega, typing.Iterable):
        # init_omega 是一个 ListLike 的对象 (List / np.ndarray)
        arr = np.array(init_omega, dtype=float)
        if len(arr.shape) != 2:
            raise ValueError("只能通过二维数组构建 Omega 矩阵，而不是 {0} 维的数组".format(len(arr.shape)))

        if arr.shape[0] != arr.shape[1]:
            raise ValueError("只能通过方阵构建 Omega 矩阵，而不是 {0} x {1} 的矩阵".format(arr.shape[0], arr.shape[1]))

        omega_mat = arr

    else:
        raise TypeError("不支持的 init_omega 类型 {0}".format(type(init_omega)))

    n_dim = omega_mat.shape[0]

    # 校验是否是对称矩阵
    for i in range(1, n_dim):
        if not np.all(np.diag(omega_mat, -i) == np.diag(omega_mat, 1)):
            raise ValueError("提供 Omega \n {0} \n 不是对称阵".format(str(omega_mat)))

    _bounds: list[BoundsType | None]
    if bounds is None:
        _bounds = [None for _ in range(n_dim)]
    elif not (isinstance(bounds, list) or isinstance(bounds, np.ndarray)):
        _bounds = [bounds]
    else:
        _bounds = [bound for bound in bounds]

    if len(_bounds) != n_dim:
        raise ValueError("指定的维数 {0} 与 bounds 的维数 {1} 不符".format(n_dim, len(_bounds)))

    try:
        names = varname(multi_vars=n_dim > 1)
    except ImproperUseError as e:
        raise ValueError("参数维度和参数赋值的数量不符，期望的参数数量为 {0}\n{1}".format(n_dim, e))

    _names: list[str] = []
    if n_dim == 1:
        if not isinstance(names, str):
            raise ValueError("单一维度构建 Omega 无法解析层多个 eta 变量")

        _names = [names]

    else:  # 校验提供的参数名数量是否足够
        if not isinstance(names, tuple):
            raise ValueError("Omega 构建需要 {0} 个 eta 变量".format(n_dim))

        if len(names) != n_dim:
            raise ValueError("参数维度和参数赋值的数量不符，期望的参数数量为 {0}".format(n_dim))

        for _name in names:
            if not isinstance(_name, str):
                raise TypeError("变量赋值只能是字符串")

            _names.append(_name)

    etas: list[Eta] = []
    omega_diag = np.diag(omega_mat)
    for index, init_value in enumerate(omega_diag):
        etas.append(Eta(name=_names[index], init_value=init_value, bounds=_bounds[index], fixed=fixed))

    omega = Omega.from_ndarray(array=omega_mat - np.diag(np.diag(omega_mat)) + np.diag(np.array(etas, dtype=object)))

    for _eta in etas:
        _eta.omega = omega

    return etas if len(etas) != 1 else etas[0]
