# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/ast_worker/if_else/_variable_mask.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 04:16 pm
#
# Last Modified: 12/09/2022 01:33 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
from typing import Any

from ...symbols import AnyContext

VariableNameType = str
IfTestVariableNameType = str
MaskedVariableNameType = str

# 实际的变量名 => list[tuple[if-条件的变量名，重命名的变量名]]
VariableMaskMappingType = dict[VariableNameType,
                                list[tuple[IfTestVariableNameType,
                                            MaskedVariableNameType]]]


def join_mask_mapping(
    left: VariableMaskMappingType, right: VariableMaskMappingType
) -> VariableMaskMappingType:
    """合并两个 masking dict"""
    result_mapping: VariableMaskMappingType = {}
    variable_names = set(left.keys()).union(right.keys())
    for var_name in variable_names:
        arr = left.get(var_name, []).copy()
        arr.extend(right.get(var_name, []))
        result_mapping[var_name] = arr

    return result_mapping


def summarize_and_eval_mask_mapping(
    mask_mapping: VariableMaskMappingType,
    local_ctx: AnyContext,
    global_ctx: AnyContext,
    no_else_fallback_var_name: dict[str, str] | None = None
) -> list[ast.stmt]:
    transformed: list[ast.stmt] = []
    # 将原变量赋值为关于所有 masked variable 的表达式
    for variable_name, branch_masks in mask_mapping.items():
        # 表达式的右边
        rhs: ast.expr | None = None

        # 所有条件变量 branch 的乘积
        coefficient_prefix: ast.expr | None = None

        __else_masked_variable_name: str | None = None
        for condition_variable_name, masked_variable_name in branch_masks:
            if condition_variable_name.startswith(
                IfElseVariableMaskTransformer.ELSE_MASKING
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
            if no_else_fallback_var_name is not None:
                __else_masked_variable_name = no_else_fallback_var_name[
                    variable_name]
            else:
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
                targets=(ast.Name(id=variable_name),), value=rhs, lineno=None
            )
        )

        local_ctx[variable_name] = eval(
            ast.unparse(rhs), global_ctx.as_dict(), local_ctx.as_dict()
        )
    return transformed


class IfElseVariableMaskTransformer(ast.NodeTransformer):
    """将需要 mask 的 variable 的 assignment 修改为 mask variable"""

    ELSE_MASKING = "__else"

    def __init__(
        self, if_node: ast.If, masking_variables: set[str], is_else: bool
    ) -> None:
        self._if_node = if_node
        self._is_else = is_else
        self._masking_variables = masking_variables
        self.mask_mp: VariableMaskMappingType = {}

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
                if target.id in self._masking_variables:
                    var_name = target.id  # 实际的变量名
                    target.id = f"{masking}__{target.id}"  # mask 后的变量名

                    if var_name not in self.mask_mp.keys():
                        self.mask_mp[var_name] = []

                    # 存储实际的变量名相关的 dict
                    self.mask_mp[var_name].append((masking, target.id))

        return node