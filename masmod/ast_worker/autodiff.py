# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/autodiff.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/01/2022 11:23 am
#
# Last Modified: 12/09/2022 02:13 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

import ast
import typing
import sympy

from .if_else import IfElseTransformer

from ..symbols import SymVar, VarContext, AnyContext
from ..translator import ASTSympyTranslator
from ..utils.mask import mask_variable


class AutoDiffNodeTransformer(ast.NodeTransformer):

    def __init__(
        self,
        source_code: str,
        var_context: VarContext[SymVar],
        self_context: AnyContext,
        local_context: AnyContext,
        global_context: AnyContext,
    ) -> None:
        self._source_code = source_code
        self._var_context = var_context

        self._local_context = local_context
        self._global_context = global_context

        self._sympy_translator = ASTSympyTranslator(
            self_context=self_context, local_context=local_context
        )

        self._partial_deriv_term_names_mapping: dict[str, list[str]] = {}

    def get_partial_deriv_term_names(self, var_name: str) -> list[str]:
        """获取生成 var_name 对应的 partial derivate 变量名

        Args:
            var_name (str): 尝试获取的 var_name

        Returns:
            list[str]: var_name 对应的 partial derivatives 的变量名
        """
        if var_name not in self._partial_deriv_term_names_mapping.keys():
            raise KeyError("{0} 没有生成对应的 partial derivative".format(var_name))
        return self._partial_deriv_term_names_mapping[var_name]

    def _append_partial_derivative(
        self, expr: sympy.Expr, var_name_prefix: str
    ) -> list[ast.Assign]:
        partial_deriv_assignments: list[ast.Assign] = []
        for var in self._var_context.values():
            if isinstance(var, SymVar):
                diff_var_name = ast.Name(
                    id=f"{var_name_prefix}_wrt_{var.name}"
                )

                if var_name_prefix not in self._partial_deriv_term_names_mapping.keys(
                ):
                    self._partial_deriv_term_names_mapping[var_name_prefix] = [
                        diff_var_name.id
                    ]
                else:
                    self._partial_deriv_term_names_mapping[
                        var_name_prefix].append(diff_var_name.id)

                partial_deriv = expr.diff(var)
                ast_expr = self._sympy_translator.translate(partial_deriv)
                partial_deriv_assignments.append(
                    ast.Assign(
                        targets=(diff_var_name,), value=ast_expr, lineno=None
                    )
                )
        return partial_deriv_assignments

    def visit_Return(self, node: ast.Return) -> typing.Any:
        return node

    def visit_If(self, node: ast.If) -> typing.Any:
        transformer = IfElseTransformer(
            source_code=self._source_code,
            global_context=self._global_context,
            local_context=self._local_context
        )
        transformed_node: typing.Any = transformer.visit(node)

        if isinstance(transformed_node, typing.Iterable):
            _node = transformed_node
        else:
            _node = [transformed_node]
        transformed: list[ast.stmt] = []

        for child_node in _node:
            if isinstance(child_node, ast.Assign):
                if child_node not in transformer.variable_hoist_transformer.hoisting_assignments.values(
                ):
                    transformed.extend(self.visit_Assign(child_node))
                else:
                    transformed.append(child_node)
            else:
                transformed.append(child_node)

        return transformed

    def visit_Assign(self, node: ast.Assign) -> typing.Any:
        lhs = node.targets

        # deal with diff
        diffs: list[ast.Assign] = []
        if len(lhs) == 1:
            token = lhs[0]
            if isinstance(token, ast.Name):
                if token.id not in self._local_context.keys():
                    rhs_expr = eval(
                        ast.unparse(node.value),
                        self._global_context.as_dict(),
                        self._local_context.as_dict()
                    )
                else:
                    rhs_expr = getattr(self._local_context, token.id)
                self._local_context[token.id] = rhs_expr

                if isinstance(rhs_expr, sympy.Expr):
                    diffs.extend(
                        self._append_partial_derivative(
                            expr=rhs_expr,
                            var_name_prefix=mask_variable(token.id)
                        )
                    )
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        return [node, *diffs]
