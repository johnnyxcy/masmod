from varname import varname
from masmod.symbols._variable import SymVar
from masmod.symbols._typings import ValueType, BoundsType

__all__ = ["theta", "Theta"]


class Theta(SymVar):
    """ 
    固定效应的变量
    """
    __slots__ = ("_mu_ref")

    @property
    def mu_ref(self) -> bool:
        # default value
        if not hasattr(self, "_mu_ref"):
            return False
        return self._mu_ref

    @mu_ref.setter
    def mu_ref(self, mu_ref: bool) -> None:
        self._mu_ref = mu_ref


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