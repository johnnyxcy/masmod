import typing
import inspect
from masmod.symbols import AnyContext, VarContext
from masmod.symbols._variable import SymVar
from masmod.symbols._covariate import Covariate


class PostInitResolver(type):

    def __call__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        """Resolve namespace"""
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj


class BaseModule(object, metaclass=PostInitResolver):

    def __init__(self) -> None:
        super().__init__()
        self._expr_context = VarContext[SymVar]()
        # TODO: const 的 context 意义真的不大
        # self._const_context = ConstContext()
        self._covariate_context = VarContext[Covariate]()
        self._global_context = AnyContext()
        self._self_context = AnyContext()

    def __post_init__(self) -> None:
        namespace = self.__dict__

        for variable_name, variable_obj in namespace.items():
            # if variable_name == "__orig_class__":
            #     # special case
            #     continue
            if isinstance(variable_obj, SymVar):
                self._expr_context[variable_name] = variable_obj
            # elif isinstance(variable_obj, int | float | bool | str):
            #     self._const_context[variable_name] = variable_obj
            elif isinstance(variable_obj, Covariate):
                self._covariate_context[variable_name] = variable_obj

        self._self_context = self._expr_context + self._covariate_context

        cls_source_file = inspect.getsourcefile(self.__class__)
        call_stacks = inspect.stack()
        for frame in call_stacks:
            if frame.filename == cls_source_file:
                f_globals = frame[0].f_globals
                for f_global_name, f_global_val in f_globals.items():
                    self._global_context[f_global_name] = f_global_val
                break
