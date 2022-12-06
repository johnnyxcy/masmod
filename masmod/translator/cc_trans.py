# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/translator/cc_trans.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/28/2022 09:47 pm
#
# Last Modified: 12/06/2022 05:15 pm
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
            raise TypeError("不支持的 const 类型: {0}".format(type(val)))

        return typ

    @classmethod
    def from_dtype(cls, dtype: typing.Any) -> ValueType:
        typ: ValueType | None = None

        if pandas.api.types.is_int64_dtype(dtype):
            typ = ValueType.VALUE_TYPE_INT
        elif pandas.api.types.is_float_dtype(dtype):
            typ = ValueType.VALUE_TYPE_DOUBLE
        if typ is None:
            raise TypeError("不支持的 dtype: {0}".format(dtype))
        return typ


Ctx = typing.Dict[str, ValueType]


@dataclass
class FuncSignature:
    args: typing.Dict[str, ValueType]  # must be in-order
    return_type: ValueType


@dataclass
class EvaluatedExpr:
    v: str
    token: ast.AST
    typ: ValueType | None = None

    def __str__(self) -> str:
        return self.v


_functor_mapper: typing.Final[typing.Dict[int, str]] = {
    id(exp): "exp", id(log): "log"
}


class CCTranslator:

    def __init__(
        self,
        cls_def: ast.ClassDef,
        trans_functions: typing.Dict[str, FuncSignature],
        source_code: str,
        var_context: VarContext[SymVar],
        covariate_context: VarContext[Covariate],
        global_context: AnyContext,
        self_context: AnyContext,
        result_variables: typing.List[str]
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

    def translate(self) -> typing.List[str]:
        """主入口，翻译 python ast => cc syntax"""
        translated: typing.List[str] = [
            *self.__include_headers(),
            "",  # empty line
            "class __Module",
            "{",
            "public:"
        ]

        for part in self._cls_def.body:
            if isinstance(part, ast.FunctionDef):
                if part.name in self._trans_functions.keys():
                    translated.extend(self._do_translate_func(part))
            else:
                self.__raise(part, NotImplementedError("尚不支持 class 功能 {0}".format(part)))

        translated.append("};")

        return translated

    def _do_translate_func(self, func_def: ast.FunctionDef) -> typing.List[str]:
        """翻译函数体"""
        translated: typing.List[str] = []

        ctx: Ctx = {}

        # 处理函数签名
        signature: FuncSignature
        if func_def.name in self._trans_functions.keys():
            signature = self._inject_self_to_signature(self._trans_functions[func_def.name])
        else:
            signature = self._extract_func_signature(func_def)

        self._assert_func_signature_is_valid(func_def, signature)

        for arg_name, arg_type in signature.args.items():
            ctx[arg_name] = arg_type

        for var_name in self._var_context.keys():
            ctx[mask_self_attr(var_name)] = ValueType.VALUE_TYPE_DOUBLE

        for cov_name, cov_obj in self._covariate_context.items():
            ctx[mask_self_attr(cov_name)] = ValueType.from_dtype(cov_obj.series.dtype)

        # for const_name, const_val in self._const_context.items():
        #     ctx[mask_self_attr(const_name)] = ValueType.from_constant(const_val)

        signature = self._inject_result_container_to_signature(signature)

        translated.extend(["", *self._do_translate_func_signature(func_def, signature), "{"])

        translated_body: typing.List[str] = [
            "", "// #region 从 self context 获取变量值", *self._retrieve_vars_from_self(), "// #endregion", ""
        ]

        # 处理函数内容
        for stmt in func_def.body:
            translated_body.extend(self._do_translate_statement(stmt, ctx))

        local_assign: typing.List[str] = ["", "// #region 将临时变量赋值至 context"]
        for var_name, var_type in ctx.items():
            if var_name not in signature.args.keys():
                translated.append(f"{var_type.value} {var_name};")
                local_assign.append(f"__local[\"{var_name}\"] = {var_name};")
        local_assign.append("// #endregion")
        translated.extend([*translated_body, *local_assign])

        translated.extend(["", "// #region 将 reserved self attr 赋值至 __container"])
        for var_index, result_var_name in enumerate(self._result_variables):
            if result_var_name not in ctx.keys():
                raise ValueError(f"没有输出 {result_var_name}")
            translated.append(f"__container({var_index}) = {result_var_name};")

        translated.extend(["// #endregion", "}"])

        return translated

    def _do_translate_statement(self, statement: ast.stmt, ctx: Ctx) -> typing.List[str]:
        """翻译 statement"""
        translated: typing.List[str] = []
        if self.__locatable(statement):
            translated.append(f"// {self._source_code_lines[statement.lineno - 1].strip()}")
        if isinstance(statement, ast.Assign):
            translated.extend(self._do_translate_assign(statement, ctx))
        elif isinstance(statement, ast.If):
            translated.extend(self._do_translate_if(statement, ctx))
        elif isinstance(statement, ast.Return):
            # special case
            # TODO: 这个会影响用户自定义 closure 函数，但是暂时不支持
            pass
        else:
            self.__raise(statement, NotImplementedError("尚不支持 statement {0}".format(statement)))

        return translated

    def _do_translate_assign(self, assign: ast.Assign, ctx: Ctx) -> typing.List[str]:
        """翻译赋值 block"""
        translated: typing.List[str] = []

        targets = assign.targets

        if len(targets) != 1:
            self.__raise(assign, ValueError("赋值变量过多，无法处理"))

        target = self._do_eval_expr(targets[0], ctx)
        value = self._do_eval_expr(assign.value, ctx)

        if value.typ is None:
            self.__raise(assign, ValueError("变量定义必须要指定类型"))

        if target.v in ctx.keys():
            _declared_typ = ctx[target.v]
            # 不允许重新定义类型
            # 特殊情况: 两个变量都是数值类型，那么使用 double 处理
            if _declared_typ != value.typ and not (_declared_typ.is_numeric() and value.typ.is_numeric()):
                self.__raise(
                    assign, TypeError("不允许重新指定变量 {0} 的类型 {1} => {2}".format(target.v, _declared_typ, value.typ))
                )
            ctx[target.v] = ValueType.VALUE_TYPE_DOUBLE
        else:
            ctx[target.v] = value.typ
        translated.append(f"{target.v} = {value.v};")
        return translated

    def _do_translate_if(self, if_: ast.If, ctx: Ctx, is_else_if: bool = False) -> typing.List[str]:
        """翻译 if block"""
        translated: typing.List[str] = []

        # if 的比较条件
        test_condition = self._do_eval_expr(if_.test, ctx)

        if test_condition.typ is None or not test_condition.typ.is_numeric():
            self.__raise(if_, TypeError("if 的比较条件必须是 bool 类型而不是 {0}".format(test_condition.typ)))

        if self.__locatable(if_):
            translated.append(f"// {self._source_code_lines[if_.lineno - 1].strip()}")

        branch_pref = "if" if not is_else_if else "else if "
        translated.extend([f"{branch_pref} ({test_condition.v})", "{"])

        # body
        for stmt in if_.body:
            translated.extend(self._do_translate_statement(stmt, ctx))

        translated.append("}")

        # 如果是 else if
        if len(if_.orelse) == 1 and isinstance(if_.orelse[0], ast.If):
            translated.extend(self._do_translate_if(if_.orelse[0], ctx, is_else_if=True))
        else:  # 如果是 else
            translated.append("else {")
            for stmt in if_.orelse:
                translated.extend(self._do_translate_statement(stmt, ctx))

            translated.append("}")

        return translated

    def _do_eval_expr(self, expr: ast.expr, ctx: Ctx) -> EvaluatedExpr:
        """处理一个表达式"""
        # 如果是个表达式，直接 eval
        if isinstance(expr, ast.Expression):
            return self._do_eval_expr(expr.body, ctx)

        # 如果是 Name
        if isinstance(expr, ast.Name):
            _identifier = expr.id
            _typ: ValueType | None = None
            # 如果在上下文有对应的类型提供，返回其类型，否则是 None
            if _identifier in ctx.keys():
                _typ = ctx[_identifier]

            return EvaluatedExpr(v=_identifier, typ=_typ, token=expr)

        # 如果是一个常数
        if isinstance(expr, ast.Constant):
            return self._do_eval_constant(expr)

        # 如果是一个比较 e.g. a > b
        if isinstance(expr, ast.Compare):
            if len(expr.ops) != 1:
                self.__raise(expr, ValueError("不支持多个 compare operator"))

            if len(expr.comparators) != 1:
                self.__raise(expr, ValueError("不支持多个比较对象"))
            left = self._do_eval_expr(expr.left, ctx)
            ops = self._do_eval_cmpop(expr.ops[0])
            right = self._do_eval_expr(expr.comparators[0], ctx)

            # TODO: add type validation for left and right
            if not left.typ or not right.typ:
                self.__raise(expr, ValueError("无法获取正确的类型"))

            # 只能比较两个数值类型或者比较符号两边的类型相同
            if not (left.typ.is_numeric() and right.typ.is_numeric()) and left.typ != right.typ:
                self.__raise(expr, TypeError("表达式两边的类型不匹配"))

            return EvaluatedExpr(v=f"{left.v} {ops.v} {right.v}", token=expr, typ=ValueType.VALUE_TYPE_INT)

        # 如果是属性访问
        if isinstance(expr, ast.Attribute):
            # 访问的对象指针
            value = self._do_eval_expr(expr.value, ctx)
            attr = expr.attr
            # 检查是否对 self 有非法访问
            if value.v == "self":
                if attr not in self._self_ctx.keys():
                    self.__raise(expr, AttributeError("对 self 的非法访问 {0}".format(attr)))

                # 获取 self 属性的类型
                obj = self._self_ctx[attr]
                typ: ValueType
                if isinstance(obj, SymVar) or isinstance(obj, Covariate):
                    typ = ctx[mask_self_attr(attr)]
                else:
                    evaluated_const = self._do_eval_constant(ast.Constant(value=obj))
                    if evaluated_const.typ is None:
                        raise ValueError("Not-Reachable")
                    typ = evaluated_const.typ

                # 由于会对 self 中的所有字段执行重新赋值，这里直接返回 attr
                return EvaluatedExpr(v=mask_self_attr(attr), typ=typ, token=expr)
            elif value.v in self._global_ctx.keys():
                return EvaluatedExpr(v=f"{value.v}.{attr}", token=expr)
            else:
                self.__raise(expr, NotImplementedError("不支持 self 以外的对象"))

        # 如果是函数调用
        if isinstance(expr, ast.Call):
            # 获取函数名称
            func = self._do_eval_expr(expr.func, ctx)

            # 获取函数参数
            args = ", ".join(map(lambda arg: self._do_eval_expr(arg, ctx).v, expr.args))

            # TODO:目前支持的函数只有 double 类型返回，如果后续有添加，重新补充逻辑
            # 如果函数名是 exp / log 这样的 reserved name
            if func in _functor_mapper.values():
                return EvaluatedExpr(v=f"{func}({args})", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr)
            elif func.v == "int":
                # cast to int

                if len(expr.args) != 1:
                    self.__raise(expr, ValueError("函数 int 只能有一个入参"))
                return EvaluatedExpr(v=f"int({args})", typ=ValueType.VALUE_TYPE_INT, token=expr)
            else:  # 或者函数的地址和 masmod.functional 一致
                func_obj = eval(func.v, self._global_ctx, {})
                if id(func_obj) in _functor_mapper.keys():
                    return EvaluatedExpr(
                        v=f"{_functor_mapper[id(func_obj)]}({args})", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr
                    )
                self.__raise(expr, ValueError("函数 {0} 无法处理".format(func)))

        # 如果是二元运算
        if isinstance(expr, ast.BinOp):
            # 左表达式
            left = self._do_eval_expr(expr.left, ctx)

            # 右表达式
            right = self._do_eval_expr(expr.right, ctx)

            # 二元运算要求左右都是数值类型，二元运算的返回值只会是 double 类型
            # special case: bool * 数值类型在乘法运算中可以被允许
            computable: bool = left.typ is not None and right.typ is not None and \
                (left.typ.is_numeric() and right.typ.is_numeric())
            if not computable:
                self.__raise(expr, ValueError("二元运算的两边必须都是数值类型"))

            # 特殊处理 pow `a ** b`
            if isinstance(expr.op, ast.Pow):
                return EvaluatedExpr(v=f"pow({left.v}, {right.v})", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr)
            else:
                op = self._do_eval_op(expr.op)
                return EvaluatedExpr(v=f"({left.v}{op.v}{right.v})", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr)

        # 如果是一元运算，即 -a, +b
        if isinstance(expr, ast.UnaryOp):
            op = self._do_eval_unaryop(typing.cast(ast.unaryop, expr.op))
            oprand = self._do_eval_expr(expr.operand, ctx)
            # 根据 oprand 的具体类型
            return EvaluatedExpr(v=f"{op.v}{oprand.v}", typ=oprand.typ, token=expr)

        self.__raise(expr, NotImplementedError("尚不支持 expression {0}".format(expr)))

    def _do_eval_constant(self, constant: ast.Constant) -> EvaluatedExpr:
        """处理常数"""
        v: str
        typ: ValueType = ValueType.from_val(constant.value)

        if typ in [ValueType.VALUE_TYPE_DOUBLE, ValueType.VALUE_TYPE_INT, ValueType.VALUE_TYPE_LONG]:
            v = str(constant.value)
        elif typ == ValueType.VALUE_TYPE_STRING:
            v = constant.value
        else:
            self.__raise(constant, NotImplementedError("暂不支持的常数类型 {0}".format(constant)))

        return EvaluatedExpr(v=v, typ=typ, token=constant)

    def _do_eval_op(self, operator: ast.operator) -> EvaluatedExpr:
        """处理二元表达式的符号 +, -, *, /"""
        if isinstance(operator, ast.Add):
            return EvaluatedExpr(v="+", token=operator)
        elif isinstance(operator, ast.Sub):
            return EvaluatedExpr(v="-", token=operator)
        elif isinstance(operator, ast.Mult):
            return EvaluatedExpr(v="*", token=operator)
        elif isinstance(operator, ast.Div):
            return EvaluatedExpr(v="/", token=operator)
        elif isinstance(operator, ast.Pow):
            self.__raise(operator, ValueError("无法通过 _do_translate_op 处理 power"))

        self.__raise(operator, NotImplementedError("尚不支持 operator {0}".format(operator)))

    def _do_eval_unaryop(self, unary_operator: ast.unaryop) -> EvaluatedExpr:
        """处理正负号 +, -"""
        if isinstance(unary_operator, ast.UAdd):
            return EvaluatedExpr(v="+", token=unary_operator)
        elif isinstance(unary_operator, ast.USub):
            return EvaluatedExpr(v="-", token=unary_operator)

        self.__raise(unary_operator, NotImplementedError("尚不支持 unary_operator {0}".format(unary_operator)))

    def _do_eval_cmpop(self, compare_operator: ast.cmpop) -> EvaluatedExpr:
        """处理比较的符号 ==, >, >=, <, <=, !="""
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
        self.__raise(compare_operator, NotImplementedError("尚不支持 compare_operator {0}".format(compare_operator)))

    def _do_translate_func_signature(self, func_def: ast.FunctionDef, signature: FuncSignature) -> typing.List[str]:
        """翻译函数签名"""
        translated: typing.List[str] = []
        if self.__locatable(func_def):
            translated.append(f"// {self._source_code_lines[func_def.lineno - 1].strip()}")

        func_signature_args: typing.List[str] = []
        for arg_name, arg_type in signature.args.items():
            signature_arg = f"{arg_type.to_cc_type()} {arg_name}"
            func_signature_args.append(signature_arg)

        func_signature_args_str = ", ".join(func_signature_args)

        translated.append(f"{signature.return_type.to_cc_type()} {func_def.name}({func_signature_args_str})")

        return translated

    def _extract_func_signature(self, func_def: ast.FunctionDef) -> FuncSignature:
        self.__raise(func_def, NotImplementedError("暂不支持用户自定义 function"))

    def _inject_self_to_signature(self, signature: FuncSignature) -> FuncSignature:
        """向函数签名中添加 self context"""
        signature_ = deepcopy(signature)
        if "self" not in signature.args.keys():
            # "self" is a special case to handle
            signature_.args = {
                "self": ValueType.VALUE_TYPE_CONTEXT_REF, **signature_.args
            }
        return signature_

    def _inject_result_container_to_signature(self, signature: FuncSignature) -> FuncSignature:
        """向函数签名中添加 __local 和 __container 参数"""
        if "__local" in signature.args.keys():
            raise ValueError("__local 是函数的预留字段，不能够用于函数签名")

        if "__container" in signature.args.keys():
            raise ValueError("__container 是函数的预留字段，不能够用于函数签名")

        signature.args["__local"] = ValueType.VALUE_TYPE_CONTEXT_REF
        signature.args["__container"] = ValueType.VALUE_TYPE_VEC_REF
        return signature

    def _assert_func_signature_is_valid(self, func_def: ast.FunctionDef, signature: FuncSignature) -> None:
        """检查函数签名是否合法"""
        for arg in func_def.args.args:
            if arg.arg not in signature.args.keys():
                self.__raise(arg, ValueError("提供的函数签名 {0} 没有包含 {1}，无法处理对应参数".format(signature, arg.arg)))

        for arg in func_def.args.kwonlyargs:
            self.__raise(arg, NotImplementedError("尚未实现 kwarg 的翻译"))

    def _retrieve_vars_from_self(self) -> typing.List[str]:
        """生成代码从 self context 中获取变量 / 协变量"""
        retrieved_vars: typing.List[str] = ["// 变量"]
        for var_name in self._var_context.keys():
            retrieved_vars.append(f"{mask_self_attr(var_name)} = std::any_cast<double>(self[\"{var_name}\"]);")

        retrieved_vars.extend(["", "// 数据集中的协变量"])
        for var_name, cov_obj in self._covariate_context.items():
            covariate_dtype = ValueType.from_dtype(cov_obj.series.dtype)
            retrieved_vars.append(
                f"{mask_self_attr(var_name)} = std::any_cast<{covariate_dtype.value}>(self[\"{var_name}\"]);"
            )

        return retrieved_vars

    def __raise(self, token: ast.AST, error: BaseException) -> typing.NoReturn:
        """重新抛出异常，并提供对应的 syntax error"""
        rethrow("\n".join(self._source_code_lines), token, error)

    def __locatable(self, token: ast.AST) -> bool:
        """检查 token 是否有 lineno 和 col offset"""
        return locatable(token)

    def __include_headers(self) -> typing.List[str]:
        """生成 include 头文件"""
        return [
            f"// Auto Generate at {datetime.now()}",
            "#include <cmath>",
            "#include <string>",
            "#include <any>",
            "#include <map>",
            "#include <Eigen/Dense>",
            "",
            "using std::exp;",
            "using std::log;",
            "using std::pow;",
            ""
        ]
