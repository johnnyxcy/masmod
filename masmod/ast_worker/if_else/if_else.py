# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/if_else/if_else.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 01:32 pm
#
# Last Modified: 12/09/2022 01:40 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
from typing import Any
import typing

from .variable_hoist import IfElseVariableHoistTransformer
from .variable_override import IfElseVariableOverrideTransformer
from ...symbols import AnyContext


class IfElseTransformer(ast.NodeTransformer):

    def __init__(
        self,
        source_code: str,
        global_context: AnyContext,
        local_context: AnyContext
    ) -> None:
        super().__init__()
        self.variable_hoist_transformer = IfElseVariableHoistTransformer(
            source_code=source_code,
            global_context=global_context,
            local_context=local_context
        )

        self.variable_override_transformer = IfElseVariableOverrideTransformer(
            source_code=source_code,
            global_context=global_context,
            local_context=local_context
        )

    def visit(self, node: ast.AST) -> Any:
        variable_hoist_transformed: list[ast.stmt] = []
        _node = self.variable_hoist_transformer.visit(node)

        if isinstance(_node, typing.Iterable):
            variable_hoist_transformed.extend(_node)
        else:
            variable_hoist_transformed.append(_node)

        variable_override_transformed: list[ast.stmt] = []
        for stmt in variable_hoist_transformed:
            transformed_stmt = self.variable_override_transformer.visit(stmt)

            if isinstance(transformed_stmt, typing.Iterable):
                variable_override_transformed.extend(transformed_stmt)
            else:
                variable_override_transformed.append(transformed_stmt)
        return variable_override_transformed
