from varname import varname
from ._variable import Variable
from ._typings import ValueType, BoundsType

__all__ = ["theta", "Theta"]


class Theta(Variable):
    """ 
    固定效应的变量
    """


def theta(init_value: ValueType | None = None, bounds: BoundsType | None = None, fixed: bool = False) -> Theta:
    """
    生成固定效应参数 Theta

    Args:
        init_value: 初值
        bounds: 上下限
        fixed: 是否固定

    Returns:
        固定效应参数 Theta
    """
    if init_value is None:
        init_value = 0.

    name = varname()

    if not isinstance(name, str):
        raise TypeError("theta 的变量只能是一个")

    return Theta(name=name, init_value=init_value, bounds=bounds, fixed=fixed)