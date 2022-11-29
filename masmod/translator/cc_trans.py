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
from masmod.utils.nanoid import generate_nanoid


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


Ctx = typing.Dict[str, ValueType]


@dataclass
class FuncSignature:
    args: typing.Dict[str, ValueType]  # must be in-order
    return_type: ValueType


@dataclass
class EvaluatedExpr:
    v: str
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
        reserved_self_attr: typing.Dict[str, ValueType],
        global_context: AnyContext,
        result_variables: typing.List[str]
    ) -> None:
        self._cls_def = cls_def
        self._trans_functions = trans_functions

        self._source_code_lines = source_code.splitlines()

        self._var_context = var_context
        self._const_context = const_context
        self._reserved_self_attr = reserved_self_attr

        self._self_ctx = (self._var_context + self._const_context).as_dict()
        for attr_name, attr_type in self._reserved_self_attr.items():
            if attr_type == ValueType.VALUE_TYPE_DOUBLE:
                self._self_ctx[attr_name] = float(0.0)
            else:
                raise NotImplementedError("暂不支持 {0} 类型的 self 属性".format(attr_type.value))

        self._global_ctx = {
            "exp": exp, "log": log, **global_context.as_dict()
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
            ctx[var_name] = ValueType.VALUE_TYPE_DOUBLE

        signature = self._inject_result_container_to_signature(signature)

        translated.extend(
            ["", "// #region 用户定义的变量", *self._do_translate_func_signature(func_def, signature), "// #endregion", ""]
        )
        translated.append("{")

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
        # for attr_index, attr_name in enumerate(self._reserved_self_attr.keys()):
        #     for var_name in ctx.keys():
        #         if var_name == attr_name:
        #             translated.append(f"__container({attr_index}, 0) = {var_name}")
        #         # else:
        #         #     re.match(r"")
        #         #     if var_name
        translated.extend(["// #endregion", ""])
        translated.append("}")

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
            return EvaluatedExpr(v=_identifier, typ=_typ)

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
                return EvaluatedExpr(v=attr, typ=typ)
            elif value.v in self._global_ctx.keys():
                return EvaluatedExpr(f"{value.v}.{attr}")
            else:
                self.__raise(expr, NotImplementedError("不支持 self 以外的对象"))
                # return f"{value}.{attr}"

        # 如果是函数调用
        if isinstance(expr, ast.Call):
            # 获取函数名称
            func = self._do_eval_expr(expr.func, ctx)

            # 获取函数参数
            args = ", ".join(map(lambda arg: self._do_eval_expr(arg, ctx).v, expr.args))

            # TODO:目前支持的函数只有 double 类型返回，如果后续有添加，重新补充逻辑
            # 如果函数名是 exp / log 这样的 reserved name
            if func in _functor_mapper.values():
                return EvaluatedExpr(v=f"{func}({args})", typ=ValueType.VALUE_TYPE_DOUBLE)
            else:  # 或者函数的地址和 masmod.functional 一致
                func_obj = eval(func.v, self._global_ctx, {})
                if id(func_obj) in _functor_mapper.keys():
                    return EvaluatedExpr(v=f"{_functor_mapper[id(func_obj)]}({args})", typ=ValueType.VALUE_TYPE_DOUBLE)
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
                return EvaluatedExpr(v=f"pow({left.v}, {right.v})", typ=ValueType.VALUE_TYPE_DOUBLE)
            else:
                op = self._do_eval_op(expr.op)
                return EvaluatedExpr(v=f"{left.v} {op.v} {right.v}", typ=ValueType.VALUE_TYPE_DOUBLE)

        # 如果是一元运算，即 -a, +b
        if isinstance(expr, ast.UnaryOp):
            op = self._do_eval_unaryop(typing.cast(ast.unaryop, expr.op))
            oprand = self._do_eval_expr(expr.operand, ctx)
            # 根据 oprand 的具体类型
            return EvaluatedExpr(v=f"{op.v}{oprand.v}", typ=oprand.typ)

        # 如果是个表达式，直接 eval
        if isinstance(expr, ast.Expression):
            return self._do_eval_expr(expr.body, ctx)

        self.__raise(expr, NotImplementedError("TODO: 支持 expression {0}".format(expr)))

    def _do_eval_constant(self, constant: ast.Constant) -> EvaluatedExpr:
        v: str
        typ: ValueType

        if isinstance(constant.value, float):
            v = str(constant.value)
            typ = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(constant.value, int):
            v = str(constant.value)
            if constant.value <= -2147483648 or constant.value >= 2147483647:
                typ = ValueType.VALUE_TYPE_LONG
            else:
                typ = ValueType.VALUE_TYPE_INT
        elif isinstance(constant.value, str):
            v = constant.value
            typ = ValueType.VALUE_TYPE_STRING
        else:
            self.__raise(constant, NotImplementedError("暂不支持的常数类型 {0}".format(constant)))

        return EvaluatedExpr(v=v, typ=typ)

    def _do_eval_op(self, operator: ast.operator) -> EvaluatedExpr:
        if isinstance(operator, ast.Add):
            return EvaluatedExpr(v="+")
        elif isinstance(operator, ast.Sub):
            return EvaluatedExpr(v="-")
        elif isinstance(operator, ast.Mult):
            return EvaluatedExpr(v="*")
        elif isinstance(operator, ast.Div):
            return EvaluatedExpr(v="/")
        elif isinstance(operator, ast.Pow):
            self.__raise(operator, ValueError("无法通过 _do_translate_op 处理 power"))

        self.__raise(operator, NotImplementedError("TODO: 支持 operator {0}".format(operator)))

    def _do_eval_unaryop(self, unary_operator: ast.unaryop) -> EvaluatedExpr:
        if isinstance(unary_operator, ast.UAdd):
            return EvaluatedExpr(v="+")
        elif isinstance(unary_operator, ast.USub):
            return EvaluatedExpr(v="-")

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
            retrieved_vars.append(f"{var_name} = std::any_cast<double>(self[\"{var_name}\"]);")
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
