# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/if_else/variable_hoist.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/07/2022 02:56 pm
#
# Last Modified: 12/08/2022 03:36 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
from typing import Any

import dataclasses

from .condition_hoist import IfElseConditionHoistTransformer
from ...symbols import AnyContext
from ...utils.rethrow import rethrow

VariableNameType = str
IfTestVariableNameType = str
MaskedVariableNameType = str

# 实际的变量名 => list[tuple[if-条件的变量名，重命名的变量名]]
HoistingMaskMappingType = dict[VariableNameType,
                                list[tuple[IfTestVariableNameType,
                                            MaskedVariableNameType]]]


@dataclasses.dataclass
class VisitIfResult:
    hoisting_assignments: dict[str, ast.Assign]
    if_node: ast.If
    hoisting_mask_mapping: HoistingMaskMappingType


def join_mask_mapping(
    left: HoistingMaskMappingType, right: HoistingMaskMappingType
) -> HoistingMaskMappingType:
    """合并两个 masking dict"""
    result_mapping: HoistingMaskMappingType = {}
    variable_names = set(left.keys()).union(right.keys())
    for var_name in variable_names:
        arr = left.get(var_name, []).copy()
        arr.extend(right.get(var_name, []))
        result_mapping[var_name] = arr

    return result_mapping


class _IfElseHoistingVariableMaskTransformer(ast.NodeTransformer):
    """将需要变量提升的 variable 的 assignment 修改为 mask variable"""

    ELSE_MASKING = "__else"

    def __init__(
        self, if_node: ast.If, hoisting: set[str], is_else: bool
    ) -> None:
        self._if_node = if_node
        self._is_else = is_else
        self._hoisting = hoisting
        self.mask_mp: HoistingMaskMappingType = {}

    def visit_Assign(self, node: ast.Assign) -> Any:
        # masking 是条件变量的名称
        test = self._if_node.test
        if not isinstance(test, ast.Name):
            raise TypeError("if 的 condition 必须 transform 为变量")
        masking = test.id

        if self._is_else:  # 如果是 else，那么 masking 就是 __{条件变量}__else
            masking = f"{self.ELSE_MASKING}{masking}"

        # 赋值的对象只能有一个值
        if len(node.targets) == 1:
            target, = node.targets
            # target 只能是 ast.Name
            if isinstance(target, ast.Name):
                # 如果是需要提升的变量
                if target.id in self._hoisting:
                    var_name = target.id  # 实际的变量名
                    target.id = f"{masking}__{target.id}"  # mask 后的变量名

                    if var_name not in self.mask_mp.keys():
                        self.mask_mp[var_name] = []

                    # 存储实际的变量名相关的 dict
                    self.mask_mp[var_name].append((masking, target.id))

        return node


class IfElseVariableHoistTransformer(ast.NodeTransformer):
    """if /else 的变量提升以及分支和的计算"""

    def __init__(
        self,
        source_code: str,
        global_context: AnyContext,
        local_context: AnyContext
    ) -> None:
        self._source_code = source_code
        self._global_ctx = global_context
        self._local_ctx = local_context

        # return values
        self.hoisting_assignments: dict[str, ast.Assign] = {}

        self.condition_branch_assignments: dict[str, ast.Assign] = {}

    def visit_If(self, node: ast.If) -> Any:
        visit_if_result = self._do_visit_if(node)

        self.hoisting_assignments = visit_if_result.hoisting_assignments

        transformed: list[ast.stmt] = [
            *visit_if_result.hoisting_assignments.values(),
            visit_if_result.if_node,
        ]

        # 将原变量赋值为关于所有 masked variable 的表达式
        for variable_name, branch_masks in visit_if_result.hoisting_mask_mapping.items():
            # 表达式的右边
            rhs: ast.expr | None = None

            # 所有条件变量 branch 的乘积
            coefficient_prefix: ast.expr | None = None

            __else_masked_variable_name: str | None = None
            for condition_variable_name, masked_variable_name in branch_masks:
                if condition_variable_name.startswith(
                    _IfElseHoistingVariableMaskTransformer.ELSE_MASKING
                ):
                    if __else_masked_variable_name is not None:
                        raise ValueError("多次定义 else block")
                    __else_masked_variable_name = masked_variable_name
                else:
                    # 如果是 if，那么他的 branch coefficient 是 (1 - b0) * (1 - b1) ... * (1 - b_k-1) * bk
                    cond = ast.Name(id=condition_variable_name)

                    if coefficient_prefix is None:
                        coefficient = cond
                    else:
                        coefficient = ast.BinOp(
                            left=coefficient_prefix, op=ast.Mult(), right=cond
                        )

                    atomic_add = ast.BinOp(
                        left=coefficient,
                        op=ast.Mult(),
                        right=ast.Name(id=masked_variable_name)
                    )

                    if rhs is None:
                        rhs = atomic_add
                    else:
                        rhs = ast.BinOp(
                            left=rhs,
                            op=ast.Add(),
                            right=ast.BinOp(
                                left=coefficient,
                                op=ast.Mult(),
                                right=ast.Name(id=masked_variable_name)
                            )
                        )

                    atomic_mult = ast.BinOp(
                        left=ast.Constant(value=1), op=ast.Sub(), right=cond
                    )
                    if coefficient_prefix is None:
                        coefficient_prefix = atomic_mult
                    else:
                        coefficient_prefix = ast.BinOp(
                            left=coefficient_prefix,
                            op=ast.Mult(),
                            right=ast.BinOp(
                                left=ast.Constant(value=1),
                                op=ast.Sub(),
                                right=cond
                            )
                        )

            if __else_masked_variable_name is None:
                raise ValueError("No Else Found")

            if rhs is None or coefficient_prefix is None:
                raise ValueError("错误的 rhs")

            rhs = ast.BinOp(
                left=rhs,
                op=ast.Add(),
                right=ast.BinOp(
                    left=coefficient_prefix,
                    op=ast.Mult(),
                    right=ast.Name(id=__else_masked_variable_name)
                )
            )

            transformed.append(
                ast.Assign(
                    targets=(ast.Name(id=variable_name),),
                    value=rhs,
                    lineno=None
                )
            )

            self._local_ctx[variable_name] = eval(
                ast.unparse(rhs),
                self._global_ctx.as_dict(),
                self._local_ctx.as_dict()
            )

        return transformed

    def _do_visit_if(self, node: ast.If) -> VisitIfResult:

        hoisting_assignments: dict[str, ast.Assign] = {}

        # 将 if 中的条件判断提出，赋值为临时变量
        condition_hoist_transformer = IfElseConditionHoistTransformer(
            self._source_code, self._global_ctx, self._local_ctx
        )
        condition_hoist_transformer.visit(node)
        self.condition_branch_assignments.update(
            condition_hoist_transformer.condition_branch_assignments
        )
        hoisting_assignments.update(
            condition_hoist_transformer.condition_branch_assignments
        )

        if not isinstance(node.test, ast.Name):
            rethrow(
                self._source_code,
                node,
                ValueError("必须要将 if 的 test hoist 为 local 变量")
            )

        if_ctx = self._local_ctx.copy()
        # 执行 if 的 body, 获取 context
        self._visit_if_body(node.body, if_ctx)
        # 检查哪些变量是新增的，如果所有的 if/else 中都有这个变量，那么需要对其执行变量提升
        hoisting_var_names = set(if_ctx.keys()) - set(self._local_ctx.keys())

        # 获取 elif/else 的变量 masking map
        orelse_hoisting_mask_mapping: HoistingMaskMappingType = {}

        if len(node.orelse) == 1 and isinstance(
            node.orelse[0], ast.If
        ):  # 如果 node.orelse 是一个 elif
            elif_visit_result = self._do_visit_if(node.orelse[0])
            hoisting_assignments.update(elif_visit_result.hoisting_assignments)
            orelse_hoisting_mask_mapping = join_mask_mapping(
                orelse_hoisting_mask_mapping,
                elif_visit_result.hoisting_mask_mapping
            )
            hoisting_var_names.intersection_update(
                elif_visit_result.hoisting_mask_mapping.keys()
            )
        elif len(node.orelse) > 0:  # 如果 node.orelse 是 else 的 body
            else_ctx = self._local_ctx.copy()

            # 处理 else 的 body
            self._visit_if_body(node.orelse, else_ctx)
            hoisting_var_names.intersection_update(
                set(else_ctx.keys()) - set(self._local_ctx.keys())
            )

            _hoist_assign, orelse_hoisting_mask_mapping = self._transform_mask_hoisting_variable(
                if_node=node,
                is_else=True,
                body=node.orelse,
                hoisting_var_names=hoisting_var_names,
                ctx=else_ctx,
                merging_mask=orelse_hoisting_mask_mapping
            )
            hoisting_assignments.update(_hoist_assign)
        else:  # 如果没有指定 else 或者 elif
            # 清空变量提升，因为有 branch 为空
            hoisting_var_names.clear()

        _hoist_assign, hoisting_mask_mapping = self._transform_mask_hoisting_variable(
            if_node=node,
            is_else=False,
            body=node.body,
            hoisting_var_names=hoisting_var_names,
            ctx=if_ctx,
            merging_mask=orelse_hoisting_mask_mapping
        )
        hoisting_assignments.update(_hoist_assign)

        return VisitIfResult(
            hoisting_assignments=hoisting_assignments,
            if_node=node,
            hoisting_mask_mapping=hoisting_mask_mapping
        )

    def _visit_if_body(self, body: list[ast.stmt], ctx: AnyContext) -> None:
        body_: list[ast.stmt] = []

        for stmt_node in body:
            if isinstance(stmt_node, ast.If):
                _transformer = IfElseVariableHoistTransformer(
                    self._source_code, self._global_ctx, ctx
                )
                transformed = _transformer.visit_If(stmt_node)
                self.condition_branch_assignments.update(
                    _transformer.condition_branch_assignments
                )
                body_.extend(transformed)
            elif isinstance(stmt_node, ast.Assign):
                self._visit_assign_within_context(stmt_node, ctx)
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

    def _transform_mask_hoisting_variable(
        self,
        if_node: ast.If,
        is_else: bool,
        body: list[ast.stmt],
        hoisting_var_names: set[str],
        ctx: AnyContext,
        merging_mask: HoistingMaskMappingType
    ) -> tuple[dict[str, ast.Assign], HoistingMaskMappingType]:
        # 使用 transformer 将 else 中需要变量提升的变量 mask 为 local 变量
        transformer = _IfElseHoistingVariableMaskTransformer(
            if_node=if_node,
            is_else=is_else,
            hoisting=hoisting_var_names,
        )
        hoisting_assignments = self._do_mask_hoisting_variable(
            transformer=transformer, body=body, ctx=ctx
        )

        # 更新 ctx 变量池
        for key in hoisting_assignments.keys():
            self._local_ctx[key] = ctx[key]

        # special case，处理条件分支
        for key in self.condition_branch_assignments.keys():
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

    def _do_mask_hoisting_variable(
        self,
        transformer: _IfElseHoistingVariableMaskTransformer,
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
