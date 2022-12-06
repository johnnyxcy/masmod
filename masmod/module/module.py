# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/module/module.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/01/2022 11:23 am
#
# Last Modified: 12/06/2022 04:31 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import abc
import inspect
import sympy
import typing
import ast
from ._base import BaseModule
from ..symbols import AnyContext, Expression
from ..ast_worker import AutoDiffNodeTransformer, FuncReturnVisitor

from ..translator.cc_trans import CCTranslator, FuncSignature, ValueType

from ..utils.mask import mask_variable
from ..utils.rethrow import rethrow


class Module(BaseModule):

    def __init__(self) -> None:
        super().__init__()
        self.__translated: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self._post_init_hook()

    @property
    def translated(self) -> str:
        if self.__translated is None:
            raise AttributeError("Invalid Attribute")
        return self.__translated

    def __getattribute__(self, __name: str) -> typing.Any:
        if __name == "pred":
            raise AttributeError("直接调用 pred() 没有意义，请尝试 TODO:提供帮助")
        return super().__getattribute__(__name)

    @abc.abstractmethod
    def pred(self, t: float) -> tuple[Expression, Expression]:
        pass

    def _post_init_hook(self) -> None:
        if "pred" not in self.__class__.__dict__:
            raise AttributeError("PredRoutine 需要指定函数 pred，请查看文档获取更多信息 TODO:")

        # TODO: check signature
        pred_signature = inspect.signature(self.__class__.__dict__["pred"])
        pred_signature_params = pred_signature.parameters.items()

        time_param_name: str | None = None

        for index, (param_name, param_obj) in enumerate(pred_signature_params):
            if index == 0 and param_name != "self":
                raise AssertionError("第一个参数必须是 self")

            if index == 1:
                if param_obj.kind != inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
                    raise AssertionError("时间参数必须是 positional or keyword")
                time_param_name = param_obj.name

        if not time_param_name:
            raise ValueError("继承的 pred 函数签名不匹配")

        pred_signature_ret_ann = pred_signature.return_annotation
        if pred_signature_ret_ann != inspect._empty:
            if pred_signature_ret_ann != tuple[Expression, Expression]:
                raise TypeError("pred 的返回值签名不匹配")
        source_code = inspect.getsource(self.__class__)
        parse_code_body = ast.parse(source_code).body
        if len(parse_code_body) != 1:
            raise ValueError("Class Def 只能有一个")
        _cls_def_ast = parse_code_body[0]
        if not isinstance(_cls_def_ast, ast.ClassDef):
            raise TypeError("source_code 不属于 Class Def 类型")

        local_context = AnyContext()
        local_context["self"] = self._self_context
        local_context["t"] = sympy.Symbol("t")
        partial_deriv_variables: typing.List[str] = []
        result_variables: list[str] = []
        for part in _cls_def_ast.body:
            # 如果是名为 "pred" 的函数, 处理 autodiff 的逻辑
            if isinstance(part, ast.FunctionDef) and part.name == "pred":
                visitor = FuncReturnVisitor(source_code)
                visitor.visit(part)

                returns = visitor.return_expr
                if not isinstance(returns.value, ast.Tuple):
                    rethrow(source_code, part, ValueError("返回值的类型错误"))

                for el in returns.value.elts:
                    if not isinstance(el, ast.Name):
                        rethrow(source_code, el, ValueError("返回值必须是赋值后的对象"))
                    result_variables.append(el.id)

                transformer = AutoDiffNodeTransformer(
                    source_code=source_code,
                    var_context=self._expr_context,
                    self_context=self._self_context,
                    local_context=local_context,
                    global_context=self._global_context
                )
                transformer.visit(part)
                for result_var_name in result_variables:
                    partial_deriv_variables.extend(
                        transformer.get_partial_deriv_term_names(mask_variable(result_var_name))
                    )

        result_variables.extend(partial_deriv_variables)

        _self_context = self._self_context.copy()
        translator = CCTranslator(
            cls_def=_cls_def_ast,
            trans_functions={
                "pred": FuncSignature(args={"t": ValueType.VALUE_TYPE_DOUBLE}, return_type=ValueType.VALUE_TYPE_VOID)
            },
            source_code=source_code,
            var_context=self._expr_context,
            covariate_context=self._covariate_context,
            self_context=_self_context,
            global_context=self._global_context,
            result_variables=result_variables
        )
        self.__translated = "\n".join(translator.translate())
