from __future__ import annotations
import ast
from copy import deepcopy
import typing
import enum
from datetime import datetime
import sympy
from dataclasses import dataclass
import re
from masmod.symbols import ExprContext, ConstContext, AnyContext
from masmod.functional import exp, log
from masmod.translator.sympy_ast_trans import SYMPY_EXP_FUNC_NAME, SYMPY_LOG_FUNC_NAME
from masmod.utils.mask_self import mask_self_attr, mask_self_get_data


class ValueType(enum.Enum):
    VALUE_TYPE_CONTEXT = "std::map<std::string, std::any>"
    VALUE_TYPE_CONTEXT_REF = "std::map<std::string, std::any>&"
    VALUE_TYPE_DOUBLE = "double"
    VALUE_TYPE_INT = "int"
    VALUE_TYPE_LONG = "long"
    VALUE_TYPE_STRING = "std::string"
    VALUE_TYPE_BOOL = "bool"
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
    def from_constant(cls, const_val: typing.Any) -> ValueType:
        typ: ValueType | None = None

        if isinstance(const_val, float):
            typ = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(const_val, bool):
            typ = ValueType.VALUE_TYPE_BOOL
        elif isinstance(const_val, int):
            if const_val <= -2147483648 or const_val >= 2147483647:
                typ = ValueType.VALUE_TYPE_LONG
            else:
                typ = ValueType.VALUE_TYPE_INT
        elif isinstance(const_val, str):
            typ = ValueType.VALUE_TYPE_STRING

        if typ is None:
            raise TypeError("不支持的 const 类型: {0}".format(type(const_val)))

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
        var_context: ExprContext,
        const_context: ConstContext,
        global_context: AnyContext,
        self_context: AnyContext,
        result_variables: typing.List[str]
    ) -> None:
        self._cls_def = cls_def
        self._trans_functions = trans_functions

        self._source_code_lines = source_code.splitlines()

        self._var_context = var_context
        self._const_context = const_context

        self._self_ctx = self_context.as_dict()
        # for attr_name, attr_type in self._reserved_self_attr.items():
        #     if attr_type == ValueType.VALUE_TYPE_DOUBLE:
        #         self._self_ctx[attr_name] = float(0.0)
        #     else:
        #         raise NotImplementedError("暂不支持 {0} 类型的 self 属性".format(attr_type.value))

        self._global_ctx = {
            "exp": exp,
            "log": log,
            SYMPY_EXP_FUNC_NAME: exp,
            SYMPY_LOG_FUNC_NAME: log,
            **global_context.as_dict(),
        }

        self._result_variables = result_variables

    # def translate(self, statements: typing.List[ast.stmt]) -> str:
    #     translated: typing.List[str] = []
    #     for stmt in statements:
    #         translated.extend(self.translate_statement(stmt))
    #     return "\n".join(translated)

    def translate(self) -> typing.List[str]:
        translated: typing.List[str] = [
            *self.__include_headers(),
            ""  # empty line
        ]

        for part in self._cls_def.body:
            if isinstance(part, ast.FunctionDef):
                if part.name in self._trans_functions.keys():
                    translated.extend(self._do_translate_func(part))
            else:
                self.__raise(part, NotImplementedError("TODO: 支持 class 功能 {0}".format(part)))

        return translated

    def _do_translate_func(self, func_def: ast.FunctionDef) -> typing.List[str]:
        translated: typing.List[str] = []

        ctx: Ctx = {}

        # process signature
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

        for const_name, const_val in self._const_context.items():
            ctx[mask_self_attr(const_name)] = ValueType.from_constant(const_val)

        signature = self._inject_result_container_to_signature(signature)

        translated.extend(["", *self._do_translate_func_signature(func_def, signature), "{"])

        translated_body: typing.List[str] = [
            "", "// #region 从 self context 获取变量值", *self._retrieve_vars_from_self(), "// #endregion", ""
        ]

        # process body
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
            found = re.findall(r"self\.(.+)", result_var_name)
            if len(found) == 1:
                result_var_name = found[0]
            if result_var_name not in ctx.keys():
                raise ValueError(f"没有输出 {result_var_name}")
            translated.append(f"__container({var_index}) = {result_var_name}")

        translated.extend(["// #endregion", "}"])

        return translated

    def _do_translate_statement(self, statement: ast.stmt, ctx: Ctx) -> typing.List[str]:
        translated: typing.List[str] = []
        if self.__locateable(statement):
            translated.append(f"// {self._source_code_lines[statement.lineno - 1].strip()}")

        if isinstance(statement, ast.Assign):
            translated.extend(self._do_translate_assign(statement, ctx))
        else:
            self.__raise(statement, NotImplementedError("TODO: 支持 statement {0}".format(statement)))

        return translated

    def _do_translate_assign(self, assign: ast.Assign, ctx: Ctx) -> typing.List[str]:
        translated: typing.List[str] = []
        targets = assign.targets

        if len(targets) != 1:
            raise ValueError()

        target = self._do_eval_expr(targets[0], ctx)
        value = self._do_eval_expr(assign.value, ctx)

        if value.typ is None:
            self.__raise(assign, ValueError("变量定义必须要指定类型"))

        if target.v in ctx.keys():
            _declared_typ = ctx[target.v]
            if _declared_typ != value.typ:
                self.__raise(assign, TypeError("不允许重新指定变量 {0} 的类型".format(target.v)))
        else:
            ctx[target.v] = value.typ
        translated.append(f"{target.v} = {value.v};")
        return translated

    def _do_eval_expr(self, expr: ast.expr, ctx: Ctx) -> EvaluatedExpr:
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
                if isinstance(obj, sympy.Expr):
                    typ = ValueType.VALUE_TYPE_DOUBLE
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
            # # self.get_data 需要做特殊处理
            # if isinstance(expr.func, ast.Attribute) and \
            #     isinstance(expr.func.value, ast.Name) and \
            #         expr.func.value.id == "self" and \
            #             expr.func.attr == "get_data":

            #     if len(expr.args) != 1:
            #         self.__raise(expr, ValueError("self.get_data 只能够有一个入参"))

            #     if not isinstance(expr.args[0], ast.Constant):
            #         self.__raise(expr.args[0], ValueError("self.get_data 只支持类似于 self.get_data(\"COL_NAME\") 的使用方式"))

            #     evaluated_arg = self._do_eval_expr(expr.args[0], ctx)
            #     evaluated_arg.
            #     mask_self_get_data()

            # 获取函数名称
            func = self._do_eval_expr(expr.func, ctx)

            # 获取函数参数
            args = ", ".join(map(lambda arg: self._do_eval_expr(arg, ctx).v, expr.args))

            # TODO:目前支持的函数只有 double 类型返回，如果后续有添加，重新补充逻辑
            # 如果函数名是 exp / log 这样的 reserved name
            if func in _functor_mapper.values():
                return EvaluatedExpr(v=f"{func}({args})", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr)
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
            if left.typ is None or right.typ is None or \
                (not left.typ.is_numeric()) or (not right.typ.is_numeric()):
                self.__raise(expr, ValueError("二元运算的两边必须都是数值类型"))

            # 特殊处理 pow `a ** b`
            if isinstance(expr.op, ast.Pow):
                return EvaluatedExpr(v=f"pow({left.v}, {right.v})", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr)
            else:
                op = self._do_eval_op(expr.op)
                return EvaluatedExpr(v=f"{left.v} {op.v} {right.v}", typ=ValueType.VALUE_TYPE_DOUBLE, token=expr)

        # 如果是一元运算，即 -a, +b
        if isinstance(expr, ast.UnaryOp):
            op = self._do_eval_unaryop(typing.cast(ast.unaryop, expr.op))
            oprand = self._do_eval_expr(expr.operand, ctx)
            # 根据 oprand 的具体类型
            return EvaluatedExpr(v=f"{op.v}{oprand.v}", typ=oprand.typ, token=expr)

        # 如果是个表达式，直接 eval
        if isinstance(expr, ast.Expression):
            return self._do_eval_expr(expr.body, ctx)

        self.__raise(expr, NotImplementedError("TODO: 支持 expression {0}".format(expr)))

    def _do_eval_constant(self, constant: ast.Constant) -> EvaluatedExpr:
        v: str
        typ: ValueType = ValueType.from_constant(constant.value)

        if typ in [ValueType.VALUE_TYPE_DOUBLE, ValueType.VALUE_TYPE_INT, ValueType.VALUE_TYPE_LONG]:
            v = str(constant.value)
        elif typ == ValueType.VALUE_TYPE_BOOL:
            v = "true" if constant.value else "false"
        elif typ == ValueType.VALUE_TYPE_STRING:
            v = constant.value
        else:
            self.__raise(constant, NotImplementedError("暂不支持的常数类型 {0}".format(constant)))

        return EvaluatedExpr(v=v, typ=typ, token=constant)

    def _do_eval_op(self, operator: ast.operator) -> EvaluatedExpr:
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

        self.__raise(operator, NotImplementedError("TODO: 支持 operator {0}".format(operator)))

    def _do_eval_unaryop(self, unary_operator: ast.unaryop) -> EvaluatedExpr:
        if isinstance(unary_operator, ast.UAdd):
            return EvaluatedExpr(v="+", token=unary_operator)
        elif isinstance(unary_operator, ast.USub):
            return EvaluatedExpr(v="-", token=unary_operator)

        self.__raise(unary_operator, NotImplementedError("TODO: 支持 unary_operator {0}".format(unary_operator)))

    def _do_translate_func_signature(self, func_def: ast.FunctionDef, signature: FuncSignature) -> typing.List[str]:
        translated: typing.List[str] = []
        if self.__locateable(func_def):
            translated.append(f"// {self._source_code_lines[func_def.lineno - 1].strip()}")

        func_signature_args: typing.List[str] = []
        for arg_name, arg_type in signature.args.items():
            signature_arg = f"{arg_type.to_cc_type()} {arg_name}"
            func_signature_args.append(signature_arg)

        func_signature_args_str = ", ".join(func_signature_args)

        translated.append(f"{signature.return_type.to_cc_type()} {func_def.name}({func_signature_args_str})")

        return translated

    def _extract_func_signature(self, func_def: ast.FunctionDef) -> FuncSignature:
        raise NotImplementedError("TODO: custom function")

    def _inject_self_to_signature(self, signature: FuncSignature) -> FuncSignature:
        signature_ = deepcopy(signature)
        if "self" not in signature.args.keys():
            # "self" is a special case to handle
            signature_.args = {
                "self": ValueType.VALUE_TYPE_CONTEXT_REF, **signature_.args
            }
        return signature_

    def _inject_result_container_to_signature(self, signature: FuncSignature) -> FuncSignature:
        if "__local" in signature.args.keys():
            raise ValueError("__local 是函数的预留字段，不能够用于函数签名")

        if "__container" in signature.args.keys():
            raise ValueError("__container 是函数的预留字段，不能够用于函数签名")

        signature.args["__local"] = ValueType.VALUE_TYPE_CONTEXT_REF
        signature.args["__container"] = ValueType.VALUE_TYPE_VEC_REF
        return signature

    def _assert_func_signature_is_valid(self, func_def: ast.FunctionDef, signature: FuncSignature) -> None:
        for arg in func_def.args.args:
            if arg.arg not in signature.args.keys():
                self.__raise(arg, ValueError("提供的函数签名 {0} 没有包含 {1}，无法处理对应参数".format(signature, arg.arg)))

        for arg in func_def.args.kwonlyargs:
            self.__raise(arg, NotImplementedError("尚未实现 kwarg 的翻译"))

    def _retrieve_vars_from_self(self) -> typing.List[str]:
        retrieved_vars: typing.List[str] = []
        for var_name in self._var_context.keys():
            retrieved_vars.append(f"{mask_self_attr(var_name)} = std::any_cast<double>(self[\"{var_name}\"]);")

        for const_name, const_val in self._const_context.items():
            val_typ = ValueType.from_constant(const_val)
            retrieved_vars.append(
                f"{mask_self_attr(const_name)} = std::any_cast<{val_typ.value}>(self[\"{const_name}\"])"
            )
        return retrieved_vars

    # def _define_self_struct(self) -> typing.List[str]:
    #     definitions: typing.List[str] = [f"struct Self_", "{", "// #region user defined attributes"]
    #     for variable_name in self._var_context.keys():
    #         definitions.append(f"double {variable_name};")

    #     definitions.extend([
    #         "// #endregion",
    #         "",  # empty line
    #         "// #region reserved attributes",
    #     ])

    #     for attr_name, attr_type in self._reserved_self_attr.items():
    #         definitions.append(f"{attr_type.value} {attr_name};")

    #     definitions.extend(["// #endregion", "}"])

    #     return definitions

    def __raise(self, token: ast.AST, error: BaseException) -> typing.NoReturn:
        if self.__locateable(token):
            lineno = token.lineno
            col_offset = token.col_offset

            orig_code = self._source_code_lines[lineno - 1]
            indicator_line = [" "] * len(orig_code)
            indicator_line[col_offset - 1] = "^"

            syntax_error_summary = "\n" + orig_code + "\n" + "".join(indicator_line)

            raise SyntaxError(syntax_error_summary) from error
        else:
            raise error

    def __locateable(self, token: ast.AST) -> bool:
        return hasattr(token, "lineno")

    def __include_headers(self) -> typing.List[str]:

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
