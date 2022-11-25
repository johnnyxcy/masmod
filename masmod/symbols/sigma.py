from __future__ import annotations

import numpy as np
import typing
from varname import varname, ImproperUseError
from dataclasses import dataclass
from .variable import Variable
from .typings import ValueType, BoundsType


class Eps(Variable):
    """
    残差的变量
    """
    __slots__ = ("_sigma")

    @property
    def sigma(self) -> Sigma:
        """
        Eps 的 Sigma 矩阵
        """
        return self._sigma

    @sigma.setter
    def sigma(self, sigma: Sigma):
        """
        设定 Eps 的 Sigma 矩阵

        Args:
            sigma: Sigma 矩阵
        """

        if not isinstance(sigma, Sigma):
            raise ValueError(f'指定的 sigma 必须是 Sigma 的实例, 传入了 {type(sigma)}')
        self._sigma = sigma


@dataclass
class SigmaBlock:
    """通过下三角矩阵构建 Sigma

    Examples:
        >>> block = SigmaBlock(
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
    tril: typing.List[ValueType] | np.ndarray  # 下三角矩阵的值 (一维数组)
    dimension: int  # block 的 dimension


class Sigma:
    """
    随机效应的矩阵
    """

    def __init__(
        self, names: typing.List[str], init_values: np.ndarray, lower_bounds: np.ndarray, upper_bounds: np.ndarray
    ) -> None:
        self.__names = names
        self.init_values = init_values
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds

    @classmethod
    def from_ndarray(cls, array: np.ndarray) -> Sigma:
        names: typing.List[str] = [_eta.name for _eta in np.diag(array)]
        init_values: np.ndarray = np.zeros(array.shape)
        lower_bounds: np.ndarray = np.zeros(array.shape)
        upper_bounds: np.ndarray = np.zeros(array.shape)

        for row in range(array.shape[0]):
            for col in range(array.shape[1]):
                cell = array[row][col]
                if isinstance(cell, Eps):
                    init_values[row][col] = cell.init_value

                    lower_bounds[row][col] = cell.bounds[0]
                    upper_bounds[row][col] = cell.bounds[1]
                else:
                    init_values[row][col] = cell
                    lower_bounds[row][col] = cell
                    upper_bounds[row][col] = cell

        return cls(names=names, init_values=init_values, lower_bounds=lower_bounds, upper_bounds=upper_bounds)

    @property
    def names(self) -> typing.List[str]:
        return self.__names


@typing.overload
def sigma(init_sigma: ValueType | None = None, bounds: BoundsType | None = None, fixed: bool = False) -> Eps:
    """生成单个 eps 对象

    Args:
        init_sigma (ValueType | None, optional): eps 的初值，默认为 1
        bounds (BoundsType | None, optional): eps 的上下限，默认为 (-inf, inf)
        fixed (bool, optional): eps 是否固定，默认为 False

    Returns:
        Eps: 单个 eps 对象
    """
    ...


@typing.overload
def sigma(
    init_sigma: SigmaBlock,
    bounds: typing.List[BoundsType | None] | np.ndarray | None = None,
    fixed: bool = False
) -> typing.List[Eps]:
    """通过下三角矩阵构建 eps 对象

    Args:
        init_sigma (SigmaBlock): 下三角矩阵
        bounds (typing.List[BoundsType] | np.ndarray | None, optional): 每个 eps 的上下限，默认所有的 eps 都为 (-inf, inf)
        fixed (bool, optional): 是否固定，如果为 True 整个下三角矩阵构建的 Sigma 都会固定，默认为 False

    Returns:
        typing.List[Eps]: 生成的多个 eps 对象
    """
    ...


@typing.overload
def sigma(
    init_sigma: typing.List[typing.List[ValueType]] | np.ndarray,
    bounds: typing.List[BoundsType | None] | np.ndarray | None = None,
    fixed: bool = False,
) -> typing.List[Eps]:
    """通过完整 Sigma 矩阵构建 eps 对象

    Args:
        init_sigma (typing.List[typing.List[ValueType]] | np.ndarray): 完整 Sigma 矩阵，必须为方块矩阵
        bounds (typing.List[BoundsType] | np.ndarray | None, optional): 每个 eps 的上下限，默认所有的 eps 都为 (-inf, inf)
        fixed (bool, optional): 是否固定，如果为 True 整个 Sigma 都会固定，默认为 False

    Returns:
        typing.List[Eps]: 生成的多个 eps 对象
    """
    ...


def sigma(
    init_sigma: ValueType | SigmaBlock | np.ndarray | typing.List[typing.List[ValueType]] | None = None,
    bounds: BoundsType | np.ndarray | typing.List[BoundsType | None] | None = None,
    fixed: bool = False
) -> Eps | typing.List[Eps]:
    sigma_mat: np.ndarray

    if init_sigma is None:
        # 默认 Sigma 构建，对角线为 1 的 1x1 Sigma 矩阵
        sigma_mat = np.array([[1]], dtype=float)
    elif isinstance(init_sigma, ValueType):
        # 单一值的 Sigma 构建，将 eps 初值放置于 1x1 Sigma 的对角线即可
        sigma_mat = np.array([[init_sigma]], dtype=float)

    elif isinstance(init_sigma, SigmaBlock):
        # 使用下三角构建 Sigma 矩阵
        tri_lower_indicies = np.tril_indices(init_sigma.dimension)
        tri_lower_len = len(tri_lower_indicies[0])
        if len(init_sigma.tril) != tri_lower_len:
            raise ValueError(
                "指定的维数 {0} 需要 {1} 个参数，与传入的参数个数 {2} 不符 ".format(
                    init_sigma.dimension, tri_lower_len, len(init_sigma.tril)
                )
            )
        tmp = np.zeros([init_sigma.dimension, init_sigma.dimension])
        tmp[tri_lower_indicies] = init_sigma.tril
        sigma_mat = tmp + tmp.T - np.diag(np.diag(tmp))

    elif isinstance(init_sigma, typing.Iterable):
        # init_sigma 是一个 ListLike 的对象 (List / np.ndarray)
        arr = np.array(init_sigma, dtype=float)
        if len(arr.shape) != 2:
            raise ValueError("只能通过二维数组构建 Sigma 矩阵，而不是 {0} 维的数组".format(len(arr.shape)))

        if arr.shape[0] != arr.shape[1]:
            raise ValueError("只能通过方阵构建 Sigma 矩阵，而不是 {0} x {1} 的矩阵".format(arr.shape[0], arr.shape[1]))

        sigma_mat = arr

    else:
        raise TypeError("不支持的 init_sigma 类型 {0}".format(type(init_sigma)))

    n_dim = sigma_mat.shape[0]

    # 校验是否是对称矩阵
    for i in range(1, n_dim):
        if not np.all(np.diag(sigma_mat, -i) == np.diag(sigma_mat, 1)):
            raise ValueError("提供 Sigma \n {0} \n 不是对称阵".format(str(sigma_mat)))

    _bounds: typing.List[BoundsType | None]
    if bounds is None:
        _bounds = [None for _ in range(n_dim)]
    elif not (isinstance(bounds, typing.List) or isinstance(bounds, np.ndarray)):
        _bounds = [bounds]
    else:
        _bounds = [bound for bound in bounds]

    if len(_bounds) != n_dim:
        raise ValueError("指定的维数 {0} 与 bounds 的维数 {1} 不符".format(n_dim, len(_bounds)))

    try:
        names = varname(multi_vars=n_dim > 1)
    except ImproperUseError as e:
        raise ValueError("参数维度和参数赋值的数量不符，期望的参数数量为 {0}\n{1}".format(n_dim, e))

    _names: typing.List[str] = []
    if n_dim == 1:
        if not isinstance(names, str):
            raise ValueError("单一维度构建 Sigma 无法解析层多个 eps 变量")

        _names = [names]

    else:  # 校验提供的参数名数量是否足够
        if not isinstance(names, tuple):
            raise ValueError("Sigma 构建需要 {0} 个 eps 变量".format(n_dim))

        if len(names) != n_dim:
            raise ValueError("参数维度和参数赋值的数量不符，期望的参数数量为 {0}".format(n_dim))

        for _name in names:
            if not isinstance(_name, str):
                raise TypeError("变量赋值只能是字符串")

            _names.append(_name)

    epsilons: typing.List[Eps] = []
    sigma_diag = np.diag(sigma_mat)
    for index, init_value in enumerate(sigma_diag):
        epsilons.append(Eps(name=_names[index], init_value=init_value, bounds=_bounds[index], fixed=fixed))

    sigma = Sigma.from_ndarray(
        array=sigma_mat - np.diag(np.diag(sigma_mat)) + np.diag(np.array(epsilons, dtype=object))
    )

    for _eta in epsilons:
        _eta.sigma = sigma

    return epsilons if len(epsilons) != 1 else epsilons[0]
