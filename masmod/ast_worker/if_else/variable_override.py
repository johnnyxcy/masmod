# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/if_else/variable_override.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 03:51 pm
#
# Last Modified: 12/09/2022 02:13 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
import dataclasses
from typing import Any

import sympy

from ._variable_mask import (
    VariableMaskMappingType,
    IfElseVariableMaskTransformer,
    join_mask_mapping,
    summarize_and_eval_mask_mapping
)
from .condition_hoist import IfElseConditionHoistTransformer
from ...symbols import AnyContext
from ...utils.rethrow import rethrow


@dataclasses.dataclass
class VisitIfResult:
    hoisting_assignments: dict[str, ast.Assign]
    if_node: ast.If
    override_mask_mapping: VariableMaskMappingType
    condition_branch_var_names: set[str]


class IfElseVariableOverrideTransformer(ast.NodeTransformer):

    def __init__(
        self,
        source_code: str,
        global_context: AnyContext,
        local_context: AnyContext
    ) -> None:
        self._source_code = source_code
        self._global_ctx = global_context
        self._local_ctx = local_context

    def visit_Assign(self, node: ast.Assign) -> Any:
        self._do_visit_assign(node, self._local_ctx)
        return node

    def visit_If(self, node: ast.If) -> Any:
        visit_if_result = self._do_visit_if(node)

        self.hoisting_assignments = visit_if_result.hoisting_assignments

        transformed: list[ast.stmt] = [
            *visit_if_result.hoisting_assignments.values(),
            visit_if_result.if_node,
        ]

        override_mask_mapping = visit_if_result.override_mask_mapping.copy()
        no_else_fallback_var_name: dict[str, str] = {}

        for override_variable_name, mp in visit_if_result.override_mask_mapping.items():
            missing_branches = visit_if_result.condition_branch_var_names.copy(
            )
            for cond_var_name, _ in mp:
                if cond_var_name in missing_branches:
                    missing_branches.remove(cond_var_name)

            for _branch in missing_branches:
                override_mask_mapping[override_variable_name].append(
                    (_branch, override_variable_name)
                )
            no_else_fallback_var_name[override_variable_name
                                     ] = override_variable_name

        transformed.extend(
            summarize_and_eval_mask_mapping(
                override_mask_mapping,
                self._local_ctx,
                self._global_ctx,
                no_else_fallback_var_name
            )
        )

        return transformed

    def _do_visit_if(self, node: ast.If) -> VisitIfResult:
        hoisting_assignments: dict[str, ast.Assign] = {}

        cond_hoist_transformer = IfElseConditionHoistTransformer(
            self._source_code, self._global_ctx, self._local_ctx
        )
        cond_hoist_transformer.visit(node)

        branches = cond_hoist_transformer.branches
        hoisting_assignments.update(
            cond_hoist_transformer.hoisting_assignments
        )

        if not isinstance(node.test, ast.Name):
            rethrow(
                self._source_code,
                node,
                ValueError("必须要将 if 的 test hoist 为 local 变量")
            )

        if_ctx = self._local_ctx.copy()
        self._visit_if_body(node.body, if_ctx)
        override_var_names: set[str] = set()
        for key in if_ctx.keys():
            if key in self._local_ctx.keys() and \
                id(self._local_ctx[key]) != id(if_ctx[key]):
                override_var_names.add(key)

        # 获取 elif/else 的变量 masking map
        orelse_override_mask_mapping: VariableMaskMappingType = {}

        if len(node.orelse) == 1 and isinstance(
            node.orelse[0], ast.If
        ):  # 如果 node.orelse 是一个 elif
            elif_visit_result = self._do_visit_if(node.orelse[0])
            hoisting_assignments.update(elif_visit_result.hoisting_assignments)
            orelse_override_mask_mapping = join_mask_mapping(
                orelse_override_mask_mapping,
                elif_visit_result.override_mask_mapping
            )
            override_var_names.union(
                elif_visit_result.override_mask_mapping.keys()
            )
        elif len(node.orelse) > 0:  # 如果 node.orelse 是 else 的 body
            else_ctx = self._local_ctx.copy()
            # 处理 else 的 body
            self._visit_if_body(node.orelse, else_ctx)
            for key in else_ctx.keys():
                if key in self._local_ctx.keys() and \
                    id(self._local_ctx[key]) != id(else_ctx[key]):
                    override_var_names.add(key)

            _hoist_assign, orelse_override_mask_mapping = self._transform_mask_override_variable(
                if_node=node,
                is_else=True,
                body=node.orelse,
                override_var_names=override_var_names,
                ctx=else_ctx,
                merging_mask=orelse_override_mask_mapping,
                condition_branch_var_names=branches
            )
            hoisting_assignments.update(_hoist_assign)
        else:  # 如果没有指定 else 或者 elif
            pass

        _hoist_assign, override_mask_mapping = self._transform_mask_override_variable(
            if_node=node,
            is_else=False,
            body=node.body,
            override_var_names=override_var_names,
            ctx=if_ctx,
            merging_mask=orelse_override_mask_mapping,
            condition_branch_var_names=branches
        )
        hoisting_assignments.update(_hoist_assign)

        return VisitIfResult(
            hoisting_assignments=hoisting_assignments,
            if_node=node,
            override_mask_mapping=override_mask_mapping,
            condition_branch_var_names=branches,
        )

    def _do_visit_assign(self, node: ast.Assign, ctx: AnyContext) -> None:
        lhs = node.targets
        if len(lhs) == 1:
            target, = lhs
            if isinstance(target, ast.Name):
                rhs = node.value
                evaluated_rhs = eval(
                    ast.unparse(rhs),
                    self._global_ctx.as_dict(),
                    ctx.as_dict()
                )

                # 如果是一个比较，需要使用符号重新处理
                if isinstance(evaluated_rhs, sympy.core.relational.Relational):
                    if target.id not in ctx.keys():
                        ctx[target.id] = sympy.Symbol(target.id)
                else:
                    ctx[target.id] = evaluated_rhs
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

    def _visit_if_body(self, body: list[ast.stmt], ctx: AnyContext) -> None:
        body_: list[ast.stmt] = []

        for stmt_node in body:
            if isinstance(stmt_node, ast.If):
                _transformer = IfElseVariableOverrideTransformer(
                    self._source_code, self._global_ctx, ctx
                )
                transformed = _transformer.visit_If(stmt_node)
                body_.extend(transformed)
            elif isinstance(stmt_node, ast.Assign):
                self._do_visit_assign(stmt_node, ctx)
                body_.append(stmt_node)
            else:
                body_.append(stmt_node)

        body.clear()
        body.extend(body_)

    def _visit_assign_within_context(
        self, node: ast.Assign, ctx: AnyContext
    ) -> None:
        # eval assignment，赋值到 ctx
        exec(ast.unparse(node), self._global_ctx.as_dict(), ctx.as_dict())

    def _transform_mask_override_variable(
        self,
        if_node: ast.If,
        is_else: bool,
        body: list[ast.stmt],
        override_var_names: set[str],
        ctx: AnyContext,
        merging_mask: VariableMaskMappingType,
        condition_branch_var_names: set[str]
    ) -> tuple[dict[str, ast.Assign], VariableMaskMappingType]:
        transformer = IfElseVariableMaskTransformer(
            if_node=if_node,
            is_else=is_else,
            masking_variables=override_var_names
        )

        hoisting_assignments = self._do_mask_override_variable(
            transformer=transformer, body=body, ctx=ctx
        )

        # 更新 ctx 变量池
        for key in hoisting_assignments.keys():
            self._local_ctx[key] = ctx[key]

        # special case，处理条件分支
        for key in condition_branch_var_names:
            if key not in self._local_ctx.keys() and key in ctx.keys():
                self._local_ctx[key] = ctx[key]
                hoisting_assignments[key] = ast.Assign(
                    targets=(ast.Name(key),),
                    value=ast.Constant(value=0),
                    lineno=None
                )

        # 合并 masking
        merged_mask = join_mask_mapping(transformer.mask_mp, merging_mask)
        return hoisting_assignments, merged_mask

    def _do_mask_override_variable(
        self,
        transformer: IfElseVariableMaskTransformer,
        body: list[ast.stmt],
        ctx: AnyContext
    ) -> dict[str, ast.Assign]:
        _hoist_assignments: dict[str, ast.Assign] = {}
        for stmt in body:
            transformer.visit(stmt)

        for _, mp in transformer.mask_mp.items():
            for _, masked_id in mp:
                _hoist_assignments[masked_id] = ast.Assign(
                    targets=(ast.Name(id=masked_id),),
                    value=ast.Constant(value=0),
                    lineno=None
                )

        for stmt in body:
            if isinstance(stmt, ast.Assign):
                lhs = stmt.targets
                if len(lhs) == 1 and isinstance(lhs[0], ast.Name):
                    target_name = lhs[0].id
                    if target_name in _hoist_assignments.keys():
                        exec(
                            ast.unparse(stmt),
                            self._global_ctx.as_dict(),
                            ctx.as_dict()
                        )

        return _hoist_assignments