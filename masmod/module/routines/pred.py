import abc
import inspect
import sympy
import typing

from ._base import BaseRoutine
from ..autodiff.pred import PredAutoDiffGenerator


class PredRoutine(BaseRoutine):

    def __init__(self) -> None:
        super().__init__()
        self._ipred: sympy.Expr | None = None
        self._y: sympy.Expr | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.register_pred()

    @property
    def ipred(self) -> sympy.Expr:
        if self._ipred is None:
            raise ValueError("self.ipred 没有定义")

        return self._ipred

    @ipred.setter
    def ipred(self, ipred: sympy.Expr | int | float) -> None:
        if isinstance(ipred, int | float):
            ipred = sympy.Float(ipred)
        elif not isinstance(ipred, sympy.Expr):
            raise TypeError("ipred 只能是 int | float | Expr 类型")

        self._ipred = ipred

    @property
    def y(self) -> sympy.Expr:
        if self._y is None:
            raise ValueError("self.y 没有定义")
        return self._y

    @y.setter
    def y(self, y: sympy.Expr | int | float) -> None:
        if isinstance(y, int | float):
            y = sympy.Float(y)
        elif not isinstance(y, sympy.Expr):
            raise TypeError("y 只能是 int | float | Expr 类型")

        self._y = y

    def __getattribute__(self, __name: str) -> typing.Any:
        if __name == "pred":
            raise AttributeError("直接调用 pred() 没有意义，请尝试 TODO:提供帮助")
        return super().__getattribute__(__name)

    @abc.abstractmethod
    def pred(self, T: float) -> None:
        pass

    def register_pred(self) -> None:
        if "pred" not in self.__class__.__dict__:
            raise AttributeError("PredRoutine 需要指定函数 pred，请查看文档获取更多信息 TODO:")

        source_code = inspect.getsource(self.__class__)
        auto_diff_gen = PredAutoDiffGenerator(
            source_code=source_code,
            expr_context=self._expr_context,
            const_context=self._const_context,
            global_context=self._global_context
        )
        auto_diff_gen.gen()
