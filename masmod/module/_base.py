import typing
from pandas import DataFrame
import sympy
import inspect
from masmod.symbols import ExprContext, ConstContext, AnyContext
from masmod.utils.mask_self import mask_self_attr, mask_self_get_data


class PostInitResolver(type):

    def __call__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        """Resolve namespace"""
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj


class BaseModule(object, metaclass=PostInitResolver):

    def __init__(self) -> None:
        super().__init__()
        self._expr_context = ExprContext()
        self._const_context = ConstContext()
        self._global_context = AnyContext()

    def __post_init__(self) -> None:
        namespace = self.__dict__

        # data 必须要提供
        if "data" not in namespace:
            raise ValueError("self.data 没有定义")

        data = namespace["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("self.data 必须是 pandas.DataFrame 数据类型")

        for col in data.columns:
            col_name = str(col)
            if col_name.find(" ") != -1:
                raise ValueError("self.data 的列名不允许包含空格 {0}".format(col_name))

        for variable_name, variable_obj in namespace.items():
            # if variable_name == "__orig_class__":
            #     # special case
            #     continue
            if isinstance(variable_obj, sympy.Expr):
                self._expr_context[variable_name] = variable_obj
            elif isinstance(variable_obj, int | float | bool | str):
                self._const_context[variable_name] = variable_obj

        _functor_context = AnyContext()

        _functor_context["get_data"] = lambda col_name: sympy.Symbol(mask_self_get_data(col_name))

        self._self_context = self._expr_context + self._const_context + _functor_context

        cls_source_file = inspect.getsourcefile(self.__class__)
        call_stacks = inspect.stack()
        for frame in call_stacks:
            if frame.filename == cls_source_file:
                f_globals = frame[0].f_globals
                for f_global_name, f_global_val in f_globals.items():
                    self._global_context[f_global_name] = f_global_val
                break

    def get_data(self, col_name: str) -> typing.Any:
        """从数据中获取某一列名的数据，这个函数会在编译阶段处理为 row-wise 的访问迭代器

        Args:
            col_name (str): 需要获取的数据列名，如果列名不存在则应该报错
        Returns:
            typing.Any: 数据中某列在某一行的值
        """
        raise NotImplementedError
