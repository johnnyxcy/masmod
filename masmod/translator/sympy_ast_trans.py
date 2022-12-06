# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/translator/sympy_ast_trans.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/30/2022 09:09 am
#
# Last Modified: 12/06/2022 04:32 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

import ast
import sympy

from ..symbols import AnyContext

SYMPY_EXP_FUNC_NAME = "__masmod__functional__exp"
SYMPY_LOG_FUNC_NAME = "__masmod__functional__log"


class ASTSympyTranslator:

    def __init__(self, local_context: AnyContext, self_context: AnyContext | None = None) -> None:
        self._self_ctx = self_context
        self._local_ctx = local_context

    def translate(self, expr: sympy.Basic) -> ast.expr:
        if isinstance(expr, sympy.Integer):
            return ast.Constant(value=int(expr))

        if isinstance(expr, sympy.Float):
            return ast.Constant(value=float(expr))

        if isinstance(expr, sympy.Symbol):
            # only allow var in context
            var_name: str | None = None

            for _var_name, _var_obj in self._local_ctx.items():
                if _var_obj == expr:
                    var_name = _var_name

            if var_name:
                return ast.Name(id=var_name)

            if self._self_ctx:
                for _var_name, _var_obj in self._self_ctx.items():
                    if _var_obj == expr:
                        var_name = _var_name
            if var_name:
                return ast.Attribute(value=ast.Name(id="self"), attr=var_name)

            raise NameError("{0} 不存在于 context 中".format(expr))

        if isinstance(expr, sympy.exp):
            exponent = expr.exp
            return ast.Call(func=ast.Name(id=SYMPY_EXP_FUNC_NAME), args=[self.translate(exponent)], keywords=[])

        if isinstance(expr, sympy.Add):
            translated: ast.AST = ast.Constant(value=0)
            for token in expr.args:
                translated = ast.BinOp(left=translated, right=self.translate(token), op=ast.Add())
            return translated

        if isinstance(expr, sympy.Mul):
            _expr: ast.AST | None = None
            for factor in expr.as_ordered_factors():
                if _expr is None:
                    _expr = self.translate(factor)
                else:
                    _expr = ast.BinOp(left=_expr, right=self.translate(factor), op=ast.Mult())

            if _expr is None:
                raise ValueError("Invalid sympy.Mul factor")

            return _expr

        if isinstance(expr, sympy.Pow):
            base, exponential = expr.args
            _base = self.translate(base)
            _exponential = self.translate(exponential)

            return ast.BinOp(left=_base, right=_exponential, op=ast.Pow())

        if isinstance(expr, sympy.core.numbers.Half):
            return ast.Constant(value=0.5)

        raise NotImplementedError("无法处理 sympy 表达式 {0}".format(str(expr)))
