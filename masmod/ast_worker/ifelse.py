import ast
from typing import Any, Literal
import sympy
import copy
import dataclasses

from masmod.symbols import AnyContext


@dataclasses.dataclass
class HoistingCondition:
    variable_name: str
    assignment: ast.Assign
    variable_symbol: sympy.Expr


VariableNameType = str
IfTestVariableNameType = str
MaskedVariableNameType = str

# 实际的变量名 => list[tuple[if-条件的变量名，重命名的变量名]]
HoistingMaskUpMappingType = dict[VariableNameType, list[tuple[IfTestVariableNameType, MaskedVariableNameType]]]


def join_mask_mapping(left: HoistingMaskUpMappingType, right: HoistingMaskUpMappingType) -> HoistingMaskUpMappingType:
    """合并两个 masking dict"""
    result_mapping: HoistingMaskUpMappingType = {}
    # for hoisting_var_name, conditional_mask_mp in left.items():
    #     for conditional_test_var_name, masked_var_name in conditional_mask_mp.items():
    #         result_mapping[hoisting_var_name][conditional_test_var_name] = masked_var_name

    variable_names = set(left.keys()).union(right.keys())
    for var_name in variable_names:
        arr = left.get(var_name, [])
        arr.extend(right.get(var_name, []))
        result_mapping[var_name] = arr

    return result_mapping


class IfElseVariableHoistingTransformer(ast.NodeTransformer):
    """将需要变量提升的 variable 的 assignment 修改为 mask variable"""

    ELSE_MASKING = "__else"
    COND_MASKING = "__bool"

    def __init__(self, if_node: ast.If | Literal["else"], hoisting: set[str]) -> None:
        self._if_node: ast.If | Literal["else"] = if_node
        self._hoisting = hoisting
        self.mask_mp: HoistingMaskUpMappingType = {}

    # def visit_If(self, node: ast.If) -> Any:
    #     transformer = IfElseVariableHoistingTransformer(if_node=node, hoisting=self._hoisting)
    #     transformer.generic_visit(node)

    #     return node

    def visit_Assign(self, node: ast.Assign) -> Any:
        masking: str
        # 如果 if 是 else，那么 masking 就是 __else
        if self._if_node == "else":
            masking = self.ELSE_MASKING
        else:  # 否则 masking 是条件变量的名称
            test = self._if_node.test
            if not isinstance(test, ast.Name):
                raise TypeError()
            masking = test.id

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


class IfElseTransformer(ast.NodeTransformer):
    """处理 if else 的变量提升"""

    def __init__(self, if_node: ast.If, global_context: AnyContext, local_context: AnyContext) -> None:
        self._if_node = if_node
        self._hoist_assignments: dict[str, ast.Assign] = {}  # must be in order
        self._global_ctx = global_context
        self._local_ctx = local_context

        self.skip_eval_assignments: list[ast.Assign] = []

    def visit_If(self, node: ast.If) -> Any:
        """如果是 if"""
        node = copy.copy(node)
        # 将 if 中的条件判断提出，赋值为临时变量
        condition = self._hoist_if_test(node)

        if not isinstance(node.test, ast.Name):
            raise ValueError("必须要将 if 的 test hoist 为 local 变量")

        # 将 if 的条件作为需要预先定义的变量
        self._hoist_assignments[condition.variable_name] = condition.assignment
        # 不需要实际 eval 这个 assignment，只有在实际运行时才会真的执行
        self.skip_eval_assignments.append(condition.assignment)
        # 将这个 if 条件的变量作为一个 symbol 处理
        self._local_ctx[condition.variable_name] = condition.variable_symbol
        if_ctx = self._local_ctx.copy()
        # 执行 if 的 body，获取 if body 中需要跳过的 evaluation
        if_skip_assignments = self._visit_if_body(node.body, if_ctx)
        # TODO: 如果是 redeclare 比如
        # a = 10
        # if true:
        #     a = 12
        # 这个方式存在问题
        # 检查哪些变量是新增的，如果所有的 if/else 中都有这个变量，那么需要对其执行变量提升
        hoisting_var_names = set(if_ctx.keys()) - set(self._local_ctx.keys())

        # 获取 elif/else 的变量 masking map
        orelse_block_hoist_masking: HoistingMaskUpMappingType = {}
        # else if block
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            elif_ = copy.copy(node.orelse[0])
            # 将 elif 的 test condition 赋值临时变量
            elif_condition = self._hoist_if_test(elif_)

            if not isinstance(elif_.test, ast.Name):
                raise ValueError("必须要将 if 的 test hoist 为 local 变量")

            # 赋值 test condition 的临时变量
            self._hoist_assignments[elif_condition.variable_name] = elif_condition.assignment
            # 跳过 test condition 赋值的 assignment evaluation
            self.skip_eval_assignments.append(elif_condition.assignment)
            # ctx 添加 test condition 的 symbol 变量
            self._local_ctx[elif_condition.variable_name] = elif_condition.variable_symbol

            elif_ctx = self._local_ctx.copy()
            # 处理 elif 的 body
            elif_skip_assignments = self._visit_if_body(elif_.body, elif_ctx)
            # 获取 elif 中额外赋值的变量，并获取与 hoisting_var_names 的交集，得到更新后的需要变量提升的变量
            hoisting_var_names.intersection_update(set(elif_ctx.keys()) - set(self._local_ctx.keys()))

            else_ctx = self._local_ctx.copy()
            # 处理 else 的 body
            else_skip_assignments = self._visit_if_body(elif_.orelse, else_ctx)
            # 获取 else 中额外赋值的变量，并获取与 hosting_var_names 的交集，更新变量提升
            hoisting_var_names.intersection_update(set(else_ctx.keys()) - set(self._local_ctx.keys()))

            # 使用 transformer 将 elif 中需要变量提升的变量 mask 为 local 变量
            elif_transformer = IfElseVariableHoistingTransformer(if_node=elif_, hoisting=hoisting_var_names)
            self._transform_if_else_variable_hoisting(
                transformer=elif_transformer, body=elif_.body, ctx=elif_ctx, skip_assignments=elif_skip_assignments
            )
            # 合并 masking
            orelse_block_hoist_masking = join_mask_mapping(orelse_block_hoist_masking, elif_transformer.mask_mp)
            # 更新 ctx 变量池
            self._local_ctx.update(elif_ctx)

            # 使用 transformer 将 else 中需要变量提升的变量 mask 为 local 变量
            else_transformer = IfElseVariableHoistingTransformer(if_node="else", hoisting=hoisting_var_names)
            self._transform_if_else_variable_hoisting(
                transformer=else_transformer, body=elif_.orelse, ctx=else_ctx, skip_assignments=else_skip_assignments
            )
            # 合并 masking
            orelse_block_hoist_masking = join_mask_mapping(orelse_block_hoist_masking, else_transformer.mask_mp)
            # 更新 ctx 变量池
            self._local_ctx.update(else_ctx)

            # 将 elif 重新赋值回 orelse 的 ast
            node.orelse[0] = elif_

        else:  # node.orelse is body part in else block
            else_ctx = self._local_ctx.copy()
            # 处理 else 的 body
            else_skip_assignments = self._visit_if_body(node.orelse, else_ctx)
            # 获取 else 中额外赋值的变量，并获取与 hosting_var_names 的交集，更新变量提升
            hoisting_var_names.intersection_update(set(else_ctx.keys()) - set(self._local_ctx.keys()))
            # 使用 transformer 将 else 中需要变量提升的变量 mask 为 local 变量
            else_transformer = IfElseVariableHoistingTransformer(if_node="else", hoisting=hoisting_var_names)
            self._transform_if_else_variable_hoisting(
                transformer=else_transformer, body=node.orelse, ctx=else_ctx, skip_assignments=else_skip_assignments
            )
            # 合并 masking
            orelse_block_hoist_masking = join_mask_mapping(orelse_block_hoist_masking, else_transformer.mask_mp)
            # 更新 ctx 变量池
            self._local_ctx.update(else_ctx)

        # 使用 transformer 将 if 中需要变量提升的变量 mask 为 local 变量
        if_body_transformer = IfElseVariableHoistingTransformer(if_node=node, hoisting=hoisting_var_names)
        self._transform_if_else_variable_hoisting(
            transformer=if_body_transformer, body=node.body, ctx=if_ctx, skip_assignments=if_skip_assignments
        )
        # 合并 masking
        hoist_masking = join_mask_mapping(if_body_transformer.mask_mp, orelse_block_hoist_masking)
        # 更新 ctx 变量池
        self._local_ctx.update(if_ctx)

        # 将提升的变量赋值，并将 if 放回 ast
        transformed: list[ast.stmt] = [*self._hoist_assignments.values(), node]

        # 将原变量赋值为关于所有 masked variable 的表达式
        for hoist_var_name, mask_mp in hoist_masking.items():
            # 表达式的右边的 ast
            rhs = ast.Constant(value=0)
            # 表达式的右边的 sympy 对象
            sympy_rhs = sympy.Number(0)
            # 所有条件变量 branch 乘积的 ast
            coef_prefix = ast.Constant(value=1)
            # 所有条件变量 branch 乘积的 sympy 对象
            sympy_coef_prefix = sympy.Number(1)
            for masking_cond, masked_var_name in mask_mp:
                # 如果是 else，那么他的 branch variable 是 (1 - b0) * (1 - b1) ... * (1 - bk)
                if masking_cond == IfElseVariableHoistingTransformer.ELSE_MASKING:  # else case
                    rhs = ast.BinOp(
                        left=rhs,
                        op=ast.Add(),
                        right=ast.BinOp(left=coef_prefix, op=ast.Mult(), right=ast.Name(id=masked_var_name))
                    )
                    sympy_rhs = sympy_rhs + sympy_coef_prefix * self._local_ctx[masked_var_name]
                else:
                    # 如果是 if，那么他的 branch variable 是 (1 - b0) * (1 - b1) ... * (1 - b_k-1) * bk
                    masking_cond_var = ast.Name(id=masking_cond)
                    coef = ast.BinOp(left=coef_prefix, op=ast.Mult(), right=masking_cond_var)
                    sympy_coef = sympy_coef_prefix * self._local_ctx[masking_cond]
                    rhs = ast.BinOp(
                        left=rhs,
                        op=ast.Add(),
                        right=ast.BinOp(left=coef, op=ast.Mult(), right=ast.Name(id=masked_var_name))
                    )
                    sympy_rhs = sympy_rhs + sympy_coef * self._local_ctx[masked_var_name]

                    coef_prefix = ast.BinOp(
                        left=coef_prefix,
                        op=ast.Mult(),
                        right=ast.BinOp(left=ast.Constant(value=1), op=ast.Sub(), right=masking_cond_var)
                    )
                    sympy_coef_prefix = sympy_coef_prefix * (1 - self._local_ctx[masking_cond])

            transformed.append(ast.Assign(targets=(ast.Name(id=hoist_var_name),), value=rhs, lineno=None))
            self._local_ctx[hoist_var_name] = sympy_rhs

        return transformed

    def _visit_if_body(self, body: list[ast.stmt], ctx: AnyContext) -> list[ast.Assign]:
        """访问 if.body block，如果 block 中有 if，那么会生成子 transformer

        Args:
            body (list[ast.stmt]): if.body
            ctx (AnyContext): 运行时的 context

        Returns:
            list[ast.Assign]: 需要忽略的 assignment
        """
        # outer_ctx = ctx.copy()

        body_: list[ast.stmt] = []
        skip_assignments: list[ast.Assign] = []
        for stmt_node in body:
            if isinstance(stmt_node, ast.If):
                _transformer = IfElseTransformer(stmt_node, self._global_ctx, ctx)
                transformed = _transformer.visit_If(stmt_node)
                skip_assignments.extend(_transformer.skip_eval_assignments)
                body_.extend(transformed)
            elif isinstance(stmt_node, ast.Assign):
                self._visit_assign_within_context(stmt_node, ctx)
                body_.append(stmt_node)
            else:
                body_.append(stmt_node)

        body.clear()
        body.extend(body_)

        return skip_assignments

        # for key in outer_ctx.keys():
        #     if id(ctx[key]) != id(outer_ctx[key]):
        #         overrides[key] = ctx[key]

    def _visit_assign_within_context(self, node: ast.Assign, ctx: AnyContext) -> None:
        if len(node.targets) == 1:
            target, = node.targets
            if isinstance(target, ast.Name):
                if target.id in ctx.keys():
                    print('11')
        # eval assignment，赋值到 ctx
        exec(ast.unparse(node), self._global_ctx.as_dict(), ctx.as_dict())

    def _transform_if_else_variable_hoisting(
        self,
        transformer: IfElseVariableHoistingTransformer,
        body: list[ast.stmt],
        ctx: AnyContext,
        skip_assignments: list[ast.Assign]
    ) -> None:
        for stmt in body:
            transformer.visit(stmt)

        # masking_conditions: set[str] = set()
        for _, mp in transformer.mask_mp.items():
            for _, masked_id in mp:
                self._hoist_assignments[masked_id] = ast.Assign(
                    targets=(ast.Name(id=masked_id),), value=ast.Constant(value=0), lineno=None
                )
                ctx[masked_id] = sympy.Symbol(masked_id)

        for stmt in body:
            if isinstance(stmt, ast.Assign) and stmt not in skip_assignments:
                exec(ast.unparse(stmt), self._global_ctx.as_dict(), ctx.as_dict())

    def _hoist_if_test(self, node: ast.If) -> HoistingCondition:
        cnt = 1
        condition_target_id = f"__bool_{cnt}"
        while condition_target_id in self._local_ctx.keys():
            cnt += 1
            condition_target_id = f"__bool_{cnt}"
        condition_symbol = sympy.Symbol(condition_target_id)
        # self._ctx[condition_target_id] = condition_symbol
        if isinstance(node.test, ast.Compare):
            pass
        elif isinstance(node.test, ast.Name):
            if node.test.id not in self._local_ctx.keys():
                raise NameError("变量名 {0} 没有定义".format(node.test.id))
        else:
            raise NotImplementedError("暂不支持的 if 判断")
        condition_assignment = ast.Assign(targets=(ast.Name(id=condition_target_id),), value=node.test, lineno=None)

        node.test = ast.Name(id=condition_target_id)
        return HoistingCondition(
            variable_name=condition_target_id, assignment=condition_assignment, variable_symbol=condition_symbol
        )
