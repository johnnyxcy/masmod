import typing
from pandas import DataFrame
import sympy

from ...symbols import ExprContext, ConstContext


class PostInitResolver(type):

    def __call__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        """Resolve namespace"""
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj


class BaseRoutine(object, metaclass=PostInitResolver):

    def __init__(self) -> None:
        super().__init__()
        self._expr_context = ExprContext()
        self._const_context = ConstContext()

    def __post_init__(self) -> None:
        namespace = self.__dict__

        # data 必须要提供
        if "data" not in namespace:
            raise ValueError("self.data 没有定义")

        data = namespace["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("self.data 必须是 pandas.DataFrame 数据类型")

        for variable_name, variable_obj in namespace.items():
            if isinstance(variable_obj, sympy.Expr):
                self._expr_context[variable_name] = variable_obj
            elif isinstance(variable_obj, int | float | bool | str):
                self._const_context[variable_name] = variable_obj

    def col(self, col_name: str) -> typing.Any:
        """从数据中获取某一列名的数据，这个函数会在编译阶段处理为 row-wise 的访问
        迭代器

        Args:
            col_name (str): 需要获取的数据列名，如果列名不存在则应该报错
        Returns:
            typing.Any: 数据中某列在某一行的值
        """
        raise AttributeError("直接调用 col() 没有意义，请尝试 TODO:提供帮助")
