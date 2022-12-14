# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/translator/cc_trans.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/28/2022 09:47 pm
#
# Last Modified: 12/09/2022 02:54 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

from __future__ import annotations
import ast
from copy import deepcopy
import typing
import enum
from datetime import datetime
from dataclasses import dataclass
import pandas.api

from .sympy_ast_trans import SYMPY_EXP_FUNC_NAME, SYMPY_LOG_FUNC_NAME
from ..symbols import VarContext, AnyContext, SymVar, Covariate
from ..functional import exp, log
from ..utils.mask import mask_self_attr
from ..utils.rethrow import locatable, rethrow


class ValueType(enum.Enum):
    VALUE_TYPE_CONTEXT = "std::map<std::string, std::any>"
    VALUE_TYPE_CONTEXT_REF = "std::map<std::string, std::any>&"
    VALUE_TYPE_DOUBLE = "double"
    VALUE_TYPE_INT = "int"
    VALUE_TYPE_LONG = "long"
    VALUE_TYPE_STRING = "std::string"
    VALUE_TYPE_VEC = "Eigen::VectorXd"
    VALUE_TYPE_VEC_REF = "Eigen::VectorXd&"
    VALUE_TYPE_MAT = "Eigen::MatrixXd"
    VALUE_TYPE_MAT_REF = "Eigen::MatrixXd&"
    VALUE_TYPE_VOID = "void"

    def to_cc_type(self) -> str:
        return self.value

    def is_numeric(self) -> bool:
        return self == self.VALUE_TYPE_DOUBLE or self == self.VALUE_TYPE_INT or self == self.VALUE_TYPE_LONG

    @classmethod
    def from_val(cls, val: typing.Any) -> ValueType:
        typ: ValueType | None = None

        if isinstance(val, float):
            typ = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(val, bool):
            typ = ValueType.VALUE_TYPE_INT
        elif isinstance(val, int):
            if val <= -2147483648 or val >= 2147483647:
                typ = ValueType.VALUE_TYPE_LONG
            else:
                typ = ValueType.VALUE_TYPE_INT
        elif isinstance(val, str):
            typ = ValueType.VALUE_TYPE_STRING

        if typ is None:
            raise TypeError("???????????? const ??????: {0}".format(type(val)))

        return typ

    @classmethod
    def from_dtype(cls, dtype: typing.Any) -> ValueType:
        typ: ValueType | None = None

        if pandas.api.types.is_int64_dtype(dtype):
            typ = ValueType.VALUE_TYPE_INT
        elif pandas.api.types.is_float_dtype(dtype):
            typ = ValueType.VALUE_TYPE_DOUBLE
        if typ is None:
            raise TypeError("???????????? dtype: {0}".format(dtype))
        return typ


Ctx = dict[str, ValueType]


@dataclass
class FuncSignature:
    args: dict[str, ValueType]  # must be in-order
    return_type: ValueType


@dataclass
class EvaluatedExpr:
    v: str
    token: ast.AST
    typ: ValueType | None = None

    def __str__(self) -> str:
        return self.v


_functor_mapper: typing.Final[dict[int, str]] = {
    id(exp): "exp", id(log): "log"
}


class CCTranslator:

    def __init__(
        self,
        cls_def: ast.ClassDef,
        trans_functions: dict[str, FuncSignature],
        source_code: str,
        var_context: VarContext[SymVar],
        covariate_context: VarContext[Covariate],
        global_context: AnyContext,
        self_context: AnyContext,
        result_variables: list[str]
    ) -> None:
        self._cls_def = cls_def
        self._trans_functions = trans_functions

        self._source_code_lines = source_code.splitlines()

        self._var_context = var_context
        self._covariate_context = covariate_context

        self._self_ctx = self_context.as_dict()
        self._global_ctx = {
            "exp": exp,
            "log": log,
            SYMPY_EXP_FUNC_NAME: exp,
            SYMPY_LOG_FUNC_NAME: log,
            **global_context.as_dict(),
        }

        self._result_variables = result_variables

    def translate(self) -> list[str]:
        """?????????????????? python ast => cc syntax"""
        translated: list[str] = [
            *self.__include_headers(),
            "",  # empty line
            "class __Module : public IModule",
            "{",
            "public:"
        ]

        for part in self._cls_def.body:
            if isinstance(part, ast.FunctionDef):
                if part.name in self._trans_functions.keys():
                    translated.extend(self._do_translate_func(part))
            else:
                self.__raise(
                    part,
                    NotImplementedError("???????????? class ?????? {0}".format(part))
                )

        translated.append("};")

        translated.extend(self.__module_factory_function())

        return translated

    def _do_translate_func(self, func_def: ast.FunctionDef) -> list[str]:
        """???????????????"""
        translated: list[str] = []

        ctx: Ctx = {}

        # ??????????????????
        signature: FuncSignature
        if func_def.name in self._trans_functions.keys():
            signature = self._inject_self_to_signature(
                self._trans_functions[func_def.name]
            )
        else:
            signature = self._extract_func_signature(func_def)

        self._assert_func_signature_is_valid(func_def, signature)

        for arg_name, arg_type in signature.args.items():
            ctx[arg_name] = arg_type

        for var_name in self._var_context.keys():
            ctx[mask_self_attr(var_name)] = ValueType.VALUE_TYPE_DOUBLE

        for cov_name, cov_obj in self._covariate_context.items():
            ctx[mask_self_attr(cov_name)
               ] = ValueType.from_dtype(cov_obj.series.dtype)

        # for const_name, const_val in self._const_context.items():
        #     ctx[mask_self_attr(const_name)] = ValueType.from_constant(const_val)

        signature = self._inject_result_container_to_signature(signature)

        translated.extend(
            ["", *self._do_translate_func_signature(func_def, signature), "{"]
        )

        translated_body: list[str] = [
            "",
            "// #region ??? self context ???????????????",
            *self._retrieve_vars_from_self(),
            "// #endregion",
            ""
        ]

        # ??????????????????
        for stmt in func_def.body:
            translated_body.extend(self._do_translate_statement(stmt, ctx))

        local_assign: list[str] = ["", "// #region ???????????????????????? context"]
        for var_name, var_type in ctx.items():
            if var_name not in signature.args.keys():
                translated.append(f"{var_type.value} {var_name};")
                local_assign.append(f"__local[\"{var_name}\"] = {var_name};")
        local_assign.append("// #endregion")
        translated.extend([*translated_body, *local_assign])

        translated.extend(
            ["", "// #region ??? reserved self attr ????????? __container"]
        )
        for var_index, result_var_name in enumerate(self._result_variables):
            if result_var_name not in ctx.keys():
                raise ValueError(f"???????????? {result_var_name}")
            translated.append(f"__container({var_index}) = {result_var_name};")

        translated.extend(["// #endregion", "}"])

        return translated

    def _do_translate_statement(self, statement: ast.stmt,
                                ctx: Ctx) -> list[str]:
        """?????? statement"""
        translated: list[str] = []
        if self.__locatable(statement):
            translated.append(
                f"// {self._source_code_lines[statement.lineno - 1].strip()}"
            )
        if isinstance(statement, ast.Assign):
            translated.extend(self._do_translate_assign(statement, ctx))
        elif isinstance(statement, ast.If):
            translated.extend(self._do_translate_if(statement, ctx))
        elif isinstance(statement, ast.Return):
            # special case
            # TODO: ?????????????????????????????? closure ??????????????????????????????
            pass
        else:
            self.__raise(
                statement,
                NotImplementedError("???????????? statement {0}".format(statement))
            )

        return translated

    def _do_translate_assign(self, assign: ast.Assign, ctx: Ctx) -> list[str]:
        """???????????? block"""
        translated: list[str] = []

        targets = assign.targets

        if len(targets) != 1:
            self.__raise(assign, ValueError("?????????????????????????????????"))

        target = self._do_eval_expr(targets[0], ctx)
        value = self._do_eval_expr(assign.value, ctx)

        if value.typ is None:
            self.__raise(assign, ValueError("?????????????????????????????????"))

        if target.v in ctx.keys():
            _declared_typ = ctx[target.v]
            # ???????????????????????????
            # ????????????: ????????????????????????????????????????????? double ??????
            if _declared_typ != value.typ and not (
                _declared_typ.is_numeric() and value.typ.is_numeric()
            ):
                self.__raise(
                    assign,
                    TypeError(
                        "??????????????????????????? {0} ????????? {1} => {2}".format(
                            target.v, _declared_typ, value.typ
                        )
                    )
                )
            ctx[target.v] = ValueType.VALUE_TYPE_DOUBLE
        else:
            ctx[target.v] = value.typ
        translated.append(f"{target.v} = {value.v};")
        return translated

    def _do_translate_if(
        self, if_: ast.If, ctx: Ctx, is_else_if: bool = False
    ) -> list[str]:
        """?????? if block"""
        translated: list[str] = []

        # if ???????????????
        test_condition = self._do_eval_expr(if_.test, ctx)

        if test_condition.typ is None or not test_condition.typ.is_numeric():
            self.__raise(
                if_,
                TypeError(
                    "if ???????????????????????? bool ??????????????? {0}".format(test_condition.typ)
                )
            )

        if self.__locatable(if_):
            translated.append(
                f"// {self._source_code_lines[if_.lineno - 1].strip()}"
            )

        branch_pref = "if" if not is_else_if else "else if "
        translated.extend([f"{branch_pref} ({test_condition.v})", "{"])

        # body
        for stmt in if_.body:
            translated.extend(self._do_translate_statement(stmt, ctx))

        translated.append("}")

        # ????????? else if
        if len(if_.orelse) == 1 and isinstance(if_.orelse[0], ast.If):
            translated.extend(
                self._do_translate_if(if_.orelse[0], ctx, is_else_if=True)
            )
        else:  # ????????? else
            translated.append("else {")
            for stmt in if_.orelse:
                translated.extend(self._do_translate_statement(stmt, ctx))

            translated.append("}")

        return translated

    def _do_eval_expr(self, expr: ast.expr, ctx: Ctx) -> EvaluatedExpr:
        """?????????????????????"""
        # ?????????????????????????????? eval
        if isinstance(expr, ast.Expression):
            return self._do_eval_expr(expr.body, ctx)

        # ????????? Name
        if isinstance(expr, ast.Name):
            _identifier = expr.id
            _typ: ValueType | None = None
            # ???????????????????????????????????????????????????????????????????????? None
            if _identifier in ctx.keys():
                _typ = ctx[_identifier]

            return EvaluatedExpr(v=_identifier, typ=_typ, token=expr)

        # ?????????????????????
        if isinstance(expr, ast.Constant):
            return self._do_eval_constant(expr)

        # ????????????????????? e.g. a > b
        if isinstance(expr, ast.Compare):
            if len(expr.ops) != 1:
                self.__raise(expr, ValueError("??????????????? compare operator"))

            if len(expr.comparators) != 1:
                self.__raise(expr, ValueError("???????????????????????????"))
            left = self._do_eval_expr(expr.left, ctx)
            ops = self._do_eval_cmpop(expr.ops[0])
            right = self._do_eval_expr(expr.comparators[0], ctx)

            # TODO: add type validation for left and right
            if not left.typ or not right.typ:
                self.__raise(expr, ValueError("???????????????????????????"))

            # ?????????????????????????????????????????????????????????????????????
            if not (
                left.typ.is_numeric() and right.typ.is_numeric()
            ) and left.typ != right.typ:
                self.__raise(expr, TypeError("?????????????????????????????????"))

            return EvaluatedExpr(
                v=f"{left.v} {ops.v} {right.v}",
                token=expr,
                typ=ValueType.VALUE_TYPE_INT
            )

        # ?????????????????????
        if isinstance(expr, ast.Attribute):
            # ?????????????????????
            value = self._do_eval_expr(expr.value, ctx)
            attr = expr.attr
            # ??????????????? self ???????????????
            if value.v == "self":
                if attr not in self._self_ctx.keys():
                    self.__raise(
                        expr, AttributeError("??? self ??????????????? {0}".format(attr))
                    )

                # ?????? self ???????????????
                obj = self._self_ctx[attr]
                typ: ValueType
                if isinstance(obj, SymVar) or isinstance(obj, Covariate):
                    typ = ctx[mask_self_attr(attr)]
                else:
                    evaluated_const = self._do_eval_constant(
                        ast.Constant(value=obj)
                    )
                    if evaluated_const.typ is None:
                        raise ValueError("Not-Reachable")
                    typ = evaluated_const.typ

                # ???????????? self ????????????????????????????????????????????????????????? attr
                return EvaluatedExpr(
                    v=mask_self_attr(attr), typ=typ, token=expr
                )
            elif value.v in self._global_ctx.keys():
                return EvaluatedExpr(v=f"{value.v}.{attr}", token=expr)
            else:
                self.__raise(expr, NotImplementedError("????????? self ???????????????"))

        # ?????????????????????
        if isinstance(expr, ast.Call):
            # ??????????????????
            func = self._do_eval_expr(expr.func, ctx)

            # ??????????????????
            args = ", ".join(
                map(lambda arg: self._do_eval_expr(arg, ctx).v, expr.args)
            )

            # TODO:??????????????????????????? double ?????????????????????????????????????????????????????????
            # ?????????????????? exp / log ????????? reserved name
            if func in _functor_mapper.values():
                return EvaluatedExpr(
                    v=f"{func}({args})",
                    typ=ValueType.VALUE_TYPE_DOUBLE,
                    token=expr
                )
            elif func.v == "int":
                # cast to int

                if len(expr.args) != 1:
                    self.__raise(expr, ValueError("?????? int ?????????????????????"))
                return EvaluatedExpr(
                    v=f"int({args})", typ=ValueType.VALUE_TYPE_INT, token=expr
                )
            else:  # ???????????????????????? masmod.functional ??????
                func_obj = eval(func.v, self._global_ctx, {})
                if id(func_obj) in _functor_mapper.keys():
                    return EvaluatedExpr(
                        v=f"{_functor_mapper[id(func_obj)]}({args})",
                        typ=ValueType.VALUE_TYPE_DOUBLE,
                        token=expr
                    )
                self.__raise(expr, ValueError("?????? {0} ????????????".format(func)))

        # ?????????????????????
        if isinstance(expr, ast.BinOp):
            # ????????????
            left = self._do_eval_expr(expr.left, ctx)

            # ????????????
            right = self._do_eval_expr(expr.right, ctx)

            # ?????????????????????????????????????????????????????????????????????????????? double ??????
            # special case: bool * ?????????????????????????????????????????????
            computable: bool = left.typ is not None and right.typ is not None and \
                (left.typ.is_numeric() and right.typ.is_numeric())
            if not computable:
                self.__raise(expr, ValueError("?????????????????????????????????????????????"))

            # ???????????? pow `a ** b`
            if isinstance(expr.op, ast.Pow):
                return EvaluatedExpr(
                    v=f"pow({left.v}, {right.v})",
                    typ=ValueType.VALUE_TYPE_DOUBLE,
                    token=expr
                )
            else:
                op = self._do_eval_op(expr.op)
                return EvaluatedExpr(
                    v=f"({left.v}{op.v}{right.v})",
                    typ=ValueType.VALUE_TYPE_DOUBLE,
                    token=expr
                )

        # ??????????????????????????? -a, +b
        if isinstance(expr, ast.UnaryOp):
            op = self._do_eval_unaryop(typing.cast(ast.unaryop, expr.op))
            oprand = self._do_eval_expr(expr.operand, ctx)
            # ?????? oprand ???????????????
            return EvaluatedExpr(
                v=f"{op.v}{oprand.v}", typ=oprand.typ, token=expr
            )

        # ?????????
        if isinstance(expr, ast.BoolOp):
            op = self._do_eval_boolop(typing.cast(ast.boolop, expr.op))

            fragments: list[str] = []
            for val in expr.values:
                fragments.append(f"({self._do_eval_expr(val, ctx).v})")

            return EvaluatedExpr(
                v=op.v.join(fragments),
                typ=ValueType.VALUE_TYPE_INT,
                token=expr
            )

        self.__raise(
            expr, NotImplementedError("???????????? expression {0}".format(expr))
        )

    def _do_eval_constant(self, constant: ast.Constant) -> EvaluatedExpr:
        """????????????"""
        v: str
        typ: ValueType = ValueType.from_val(constant.value)

        if typ in [
            ValueType.VALUE_TYPE_DOUBLE,
            ValueType.VALUE_TYPE_INT,
            ValueType.VALUE_TYPE_LONG
        ]:
            v = str(constant.value)
        elif typ == ValueType.VALUE_TYPE_STRING:
            v = constant.value
        else:
            self.__raise(
                constant,
                NotImplementedError("??????????????????????????? {0}".format(constant))
            )

        return EvaluatedExpr(v=v, typ=typ, token=constant)

    def _do_eval_op(self, operator: ast.operator) -> EvaluatedExpr:
        """?????????????????????????????? +, -, *, /"""
        if isinstance(operator, ast.Add):
            return EvaluatedExpr(v="+", token=operator)
        elif isinstance(operator, ast.Sub):
            return EvaluatedExpr(v="-", token=operator)
        elif isinstance(operator, ast.Mult):
            return EvaluatedExpr(v="*", token=operator)
        elif isinstance(operator, ast.Div):
            return EvaluatedExpr(v="/", token=operator)
        elif isinstance(operator, ast.Pow):
            self.__raise(
                operator, ValueError("???????????? _do_translate_op ?????? power")
            )

        self.__raise(
            operator,
            NotImplementedError("???????????? operator {0}".format(operator))
        )

    def _do_eval_boolop(self, bool_operator: ast.boolop) -> EvaluatedExpr:
        if isinstance(bool_operator, ast.And):
            return EvaluatedExpr(v="&&", token=bool_operator)
        elif isinstance(bool_operator, ast.Or):
            return EvaluatedExpr(v="||", token=bool_operator)

        self.__raise(
            bool_operator,
            NotImplementedError(
                "???????????? bool_operator {0}".format(bool_operator)
            )
        )

    def _do_eval_unaryop(self, unary_operator: ast.unaryop) -> EvaluatedExpr:
        """??????????????? +, -"""
        if isinstance(unary_operator, ast.UAdd):
            return EvaluatedExpr(v="+", token=unary_operator)
        elif isinstance(unary_operator, ast.USub):
            return EvaluatedExpr(v="-", token=unary_operator)

        self.__raise(
            unary_operator,
            NotImplementedError(
                "???????????? unary_operator {0}".format(unary_operator)
            )
        )

    def _do_eval_cmpop(self, compare_operator: ast.cmpop) -> EvaluatedExpr:
        """????????????????????? ==, >, >=, <, <=, !="""
        if isinstance(compare_operator, ast.Eq):
            return EvaluatedExpr(v="==", token=compare_operator)
        elif isinstance(compare_operator, ast.Gt):
            return EvaluatedExpr(v=">", token=compare_operator)
        elif isinstance(compare_operator, ast.GtE):
            return EvaluatedExpr(v=">=", token=compare_operator)
        elif isinstance(compare_operator, ast.Lt):
            return EvaluatedExpr(v="<", token=compare_operator)
        elif isinstance(compare_operator, ast.LtE):
            return EvaluatedExpr(v="<=", token=compare_operator)
        elif isinstance(compare_operator, ast.NotEq):
            return EvaluatedExpr(v="!=", token=compare_operator)
        self.__raise(
            compare_operator,
            NotImplementedError(
                "???????????? compare_operator {0}".format(compare_operator)
            )
        )

    def _do_translate_func_signature(
        self, func_def: ast.FunctionDef, signature: FuncSignature
    ) -> list[str]:
        """??????????????????"""
        translated: list[str] = []
        if self.__locatable(func_def):
            translated.append(
                f"// {self._source_code_lines[func_def.lineno - 1].strip()}"
            )

        func_signature_args: list[str] = []
        for arg_name, arg_type in signature.args.items():
            signature_arg = f"{arg_type.to_cc_type()} {arg_name}"
            func_signature_args.append(signature_arg)

        func_signature_args_str = ", ".join(func_signature_args)

        translated.append(
            f"{signature.return_type.to_cc_type()} {func_def.name}({func_signature_args_str})"
        )

        return translated

    def _extract_func_signature(
        self, func_def: ast.FunctionDef
    ) -> FuncSignature:
        self.__raise(func_def, NotImplementedError("??????????????????????????? function"))

    def _inject_self_to_signature(
        self, signature: FuncSignature
    ) -> FuncSignature:
        """???????????????????????? self context"""
        signature_ = deepcopy(signature)
        if "self" not in signature.args.keys():
            # "self" is a special case to handle
            signature_.args = {
                "self": ValueType.VALUE_TYPE_CONTEXT_REF, **signature_.args
            }
        return signature_

    def _inject_result_container_to_signature(
        self, signature: FuncSignature
    ) -> FuncSignature:
        """???????????????????????? __local ??? __container ??????"""
        if "__local" in signature.args.keys():
            raise ValueError("__local ??????????????????????????????????????????????????????")

        if "__container" in signature.args.keys():
            raise ValueError("__container ??????????????????????????????????????????????????????")

        signature.args["__local"] = ValueType.VALUE_TYPE_CONTEXT_REF
        signature.args["__container"] = ValueType.VALUE_TYPE_VEC_REF
        return signature

    def _assert_func_signature_is_valid(
        self, func_def: ast.FunctionDef, signature: FuncSignature
    ) -> None:
        """??????????????????????????????"""
        for arg in func_def.args.args:
            if arg.arg not in signature.args.keys():
                self.__raise(
                    arg,
                    ValueError(
                        "????????????????????? {0} ???????????? {1}???????????????????????????".format(
                            signature, arg.arg
                        )
                    )
                )

        for arg in func_def.args.kwonlyargs:
            self.__raise(arg, NotImplementedError("???????????? kwarg ?????????"))

    def _retrieve_vars_from_self(self) -> list[str]:
        """??????????????? self context ??????????????? / ?????????"""
        retrieved_vars: list[str] = ["// ??????"]
        for var_name in self._var_context.keys():
            retrieved_vars.append(
                f"{mask_self_attr(var_name)} = std::any_cast<double>(self[\"{var_name}\"]);"
            )

        retrieved_vars.extend(["", "// ????????????????????????"])
        for var_name, cov_obj in self._covariate_context.items():
            covariate_dtype = ValueType.from_dtype(cov_obj.series.dtype)
            retrieved_vars.append(
                f"{mask_self_attr(var_name)} = std::any_cast<{covariate_dtype.value}>(self[\"{var_name}\"]);"
            )

        return retrieved_vars

    def __raise(self, token: ast.AST, error: BaseException) -> typing.NoReturn:
        """??????????????????????????????????????? syntax error"""
        rethrow("\n".join(self._source_code_lines), token, error)

    def __locatable(self, token: ast.AST) -> bool:
        """?????? token ????????? lineno ??? col offset"""
        return locatable(token)

    def __include_headers(self) -> list[str]:
        """?????? include ?????????"""
        return [
            f"// Auto Generate at {datetime.now()}",
            "#include <cmath>",
            "#include <string>",
            "#include <any>",
            "#include <map>",
            "#include <Eigen/Dense>",
            "#include \"masmod/libc/headers.hpp\"",
            "",
            "using std::exp;",
            "using std::log;",
            "using std::pow;",
            "using masmod::libc::modules::IModule;"
            ""
        ]

    def __module_factory_function(self) -> list[str]:
        """?????? module factory ????????????"""
        return [
            "",
            "__DYLIB_EXPORT IModule* __dylib_module_factory()",
            "{",
            "return new __Module();",
            "}",
            ""
        ]
