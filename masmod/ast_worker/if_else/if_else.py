# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/if_else/if_else.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 01:32 pm
#
# Last Modified: 12/08/2022 01:57 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
from typing import Any

from .variable_hoist import IfElseVariableHoistTransformer
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

    def visit(self, node: ast.AST) -> Any:
        node = self.variable_hoist_transformer.visit(node)

        return node