# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/if_else/condition_hoist.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/07/2022 03:00 pm
#
# Last Modified: 12/09/2022 01:20 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

import ast
import sympy
from typing import Any

from ...symbols import AnyContext
from ...utils.rethrow import rethrow


class IfElseConditionHoistTransformer(ast.NodeTransformer):
    """将 if / else 的 condition 赋值为变量
    
    * 这个只能处理一层的逻辑，不支持 nested
    """

    COND_MASKING = "__bool"

    def __init__(
        self,
        source_code: str,
        global_context: AnyContext,
        local_context: AnyContext
    ) -> None:
        self._source_code = source_code
        self._global_context = global_context
        self._local_ctx = local_context

        self.branches: set[str] = set()
        # dict[condition-variable-name => assignment-ast-token]
        self.hoisting_assignments: dict[str, ast.Assign] = {}

    def visit_Assign(self, node: ast.Assign) -> Any:
        # 通过 exec 更新 context
        exec(
            ast.unparse(node),
            self._global_context.as_dict(),
            self._local_ctx.as_dict()
        )
        return node

    def visit_If(self, node: ast.If) -> Any:
        self.hoisting_assignments = self._do_visit_if(node)
        self.branches.update(self.hoisting_assignments.keys())

        return [*self.hoisting_assignments.values(), node]

    def _do_visit_if(self, node: ast.If) -> dict[str, ast.Assign]:
        hoisted_assignments: dict[str, ast.Assign] = {}

        if isinstance(node.test, ast.Compare):
            # 尝试命名 if 条件的变量
            cnt = 1
            condition_target_id = f"{self.COND_MASKING}_{cnt}"
            while condition_target_id in self._local_ctx.keys():
                cnt += 1
                condition_target_id = f"{self.COND_MASKING}_{cnt}"

            # 以符号代替运行时 eval
            condition_symbol = sympy.Symbol(condition_target_id)

            # 将 node.test 赋值至 condition_target_id
            condition_assignment = ast.Assign(
                targets=(ast.Name(id=condition_target_id),),
                value=node.test,
                lineno=None
            )

            # 补充赋值语句至 hoisted_assignments
            hoisted_assignments[condition_target_id] = condition_assignment

            node.test = ast.Name(id=condition_target_id)
            self._local_ctx[condition_target_id] = condition_symbol
        elif isinstance(node.test, ast.Name):
            # 检查如果 node.test 是变量的话，是否正确的存在于 context 中
            if node.test.id not in self._local_ctx.keys():
                rethrow(
                    self._source_code,
                    node,
                    NameError("变量名 {0} 没有定义".format(node.test.id))
                )
            self.branches.add(node.test.id)
        else:
            rethrow(
                self._source_code, node, NotImplementedError("暂不支持的 if 判断")
            )

        # 如果是 elif 的话递归处理 elif 的 condition 赋值
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            hoisted_assignments.update(self._do_visit_if(node.orelse[0]))

        return hoisted_assignments
