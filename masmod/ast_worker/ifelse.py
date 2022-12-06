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

HoistingMaskUpMappingType = dict[VariableNameType, list[tuple[IfTestVariableNameType, MaskedVariableNameType]]]


def join_mask_mapping(left: HoistingMaskUpMappingType, right: HoistingMaskUpMappingType) -> HoistingMaskUpMappingType:
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

    ELSE_MASKING = "__else"
    COND_MASKING = "__bool"

    def __init__(self, if_node: ast.If | Literal["else"], hoisting: set[str]) -> None:
        self._if_node: ast.If | Literal["else"] = if_node
        self._hoisting = hoisting
        self.mask_mp: HoistingMaskUpMappingType = {}

    def visit_Assign(self, node: ast.Assign) -> Any:
        masking: str
        if self._if_node == "else":
            masking = self.ELSE_MASKING
        else:
            test = self._if_node.test
            if not isinstance(test, ast.Name):
                raise TypeError()
            masking = test.id

        if len(node.targets) == 1:
            target, = node.targets
            if isinstance(target, ast.Name):
                if target.id in self._hoisting:
                    var_name = target.id
                    target.id = f"{masking}__{target.id}"

                    if var_name not in self.mask_mp.keys():
                        self.mask_mp[var_name] = []

                    self.mask_mp[var_name].append((masking, target.id))

        return node


class IfElseTransformer(ast.NodeTransformer):

    def __init__(self, global_context: AnyContext, local_context: AnyContext) -> None:
        self._hoist_assignments: dict[str, ast.Assign] = {}  # must be in order
        self._global_ctx = global_context
        self._local_ctx = local_context

        self.skip_eval_assignments: list[ast.Assign] = []

    def visit_If(self, node: ast.If) -> Any:
        node = copy.copy(node)
        condition = self._hoist_if_test(node)

        if not isinstance(node.test, ast.Name):
            raise ValueError("必须要将 if 的 test hoist 为 local 变量")

        self._hoist_assignments[condition.variable_name] = condition.assignment
        self.skip_eval_assignments.append(condition.assignment)
        self._local_ctx[condition.variable_name] = condition.variable_symbol
        if_ctx = self._local_ctx.copy()
        self._visit_if_body(node.body, if_ctx)
        # TODO: 如果是 redeclare 比如
        # a = 10
        # if true:
        #     a = 12
        # 这个方式存在问题
        hoisting_var_names = set(if_ctx.keys()) - set(self._local_ctx.keys())

        orelse_block_hoist_masking: HoistingMaskUpMappingType = {}
        # else if block
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            elif_ = copy.copy(node.orelse[0])
            elif_condition = self._hoist_if_test(elif_)

            if not isinstance(elif_.test, ast.Name):
                raise ValueError("必须要将 if 的 test hoist 为 local 变量")

            self._hoist_assignments[elif_condition.variable_name] = elif_condition.assignment
            self.skip_eval_assignments.append(elif_condition.assignment)
            self._local_ctx[elif_condition.variable_name] = elif_condition.variable_symbol

            elif_ctx = self._local_ctx.copy()
            self._visit_if_body(elif_.body, elif_ctx)
            hoisting_var_names.intersection_update(set(elif_ctx.keys()) - set(self._local_ctx.keys()))

            else_ctx = self._local_ctx.copy()
            self._visit_if_body(elif_.orelse, else_ctx)
            hoisting_var_names.intersection_update(set(else_ctx.keys()) - set(self._local_ctx.keys()))

            elif_transformer = IfElseVariableHoistingTransformer(if_node=elif_, hoisting=hoisting_var_names)
            self._transform_if_else_variable_hoisting(
                transformer=elif_transformer, body=elif_.body, ctx=self._local_ctx
            )
            orelse_block_hoist_masking = join_mask_mapping(orelse_block_hoist_masking, elif_transformer.mask_mp)

            else_transformer = IfElseVariableHoistingTransformer(if_node="else", hoisting=hoisting_var_names)
            self._transform_if_else_variable_hoisting(
                transformer=else_transformer, body=elif_.orelse, ctx=self._local_ctx
            )
            orelse_block_hoist_masking = join_mask_mapping(orelse_block_hoist_masking, else_transformer.mask_mp)

            node.orelse[0] = elif_

        else:  # node.orelse is body part in else block
            else_ctx = self._local_ctx.copy()
            self._visit_if_body(node.orelse, else_ctx)
            hoisting_var_names.intersection_update(set(else_ctx.keys()) - set(self._local_ctx.keys()))
            else_transformer = IfElseVariableHoistingTransformer(if_node="else", hoisting=hoisting_var_names)
            self._transform_if_else_variable_hoisting(
                transformer=else_transformer, body=node.orelse, ctx=self._local_ctx
            )

            orelse_block_hoist_masking = join_mask_mapping(orelse_block_hoist_masking, else_transformer.mask_mp)

        if_body_transformer = IfElseVariableHoistingTransformer(if_node=node, hoisting=hoisting_var_names)
        self._transform_if_else_variable_hoisting(transformer=if_body_transformer, body=node.body, ctx=self._local_ctx)
        hoist_masking = join_mask_mapping(if_body_transformer.mask_mp, orelse_block_hoist_masking)

        transformed: list[ast.stmt] = [*self._hoist_assignments.values(), node]

        for hoist_var_name, mask_mp in hoist_masking.items():
            rhs = ast.Constant(value=0)
            sympy_rhs = sympy.Number(0)
            coef_prefix = ast.Constant(value=1)
            sympy_coef_prefix = sympy.Number(1)
            for masking_cond, masked_var_name in mask_mp:
                if masking_cond == IfElseVariableHoistingTransformer.ELSE_MASKING:  # else case
                    rhs = ast.BinOp(
                        left=rhs,
                        op=ast.Add(),
                        right=ast.BinOp(left=coef_prefix, op=ast.Mult(), right=ast.Name(id=masked_var_name))
                    )
                    sympy_rhs = sympy_rhs + sympy_coef_prefix * getattr(self._local_ctx, masked_var_name)
                else:
                    masking_cond_var = ast.Name(id=masking_cond)
                    coef = ast.BinOp(left=coef_prefix, op=ast.Mult(), right=masking_cond_var)
                    sympy_coef = sympy_coef_prefix * getattr(self._local_ctx, masking_cond)
                    rhs = ast.BinOp(
                        left=rhs,
                        op=ast.Add(),
                        right=ast.BinOp(left=coef, op=ast.Mult(), right=ast.Name(id=masked_var_name))
                    )
                    sympy_rhs = sympy_rhs + sympy_coef * getattr(self._local_ctx, masked_var_name)
                    coef_prefix = ast.BinOp(
                        left=coef_prefix,
                        op=ast.Mult(),
                        right=ast.BinOp(left=ast.Constant(value=1), op=ast.Sub(), right=masking_cond_var)
                    )
                    sympy_coef_prefix = sympy_coef_prefix * (1 - getattr(self._local_ctx, masking_cond))

            transformed.append(ast.Assign(targets=(ast.Name(id=hoist_var_name),), value=rhs, lineno=None))
            self._local_ctx[hoist_var_name] = sympy_rhs

        return transformed

    def _visit_if_body(self, body: list[ast.stmt], ctx: AnyContext) -> None:
        for stmt_node in body:
            if isinstance(stmt_node, ast.If):
                _transformer = IfElseTransformer(self._global_ctx, ctx)
                _transformer.visit(stmt_node)
            elif isinstance(stmt_node, ast.Assign):
                self._visit_assign_within_context(stmt_node, ctx)

    def _visit_assign_within_context(self, node: ast.Assign, ctx: AnyContext) -> None:
        exec(ast.unparse(node), self._global_ctx.as_dict(), ctx.as_dict())

    def _transform_if_else_variable_hoisting(
        self, transformer: IfElseVariableHoistingTransformer, body: list[ast.stmt], ctx: AnyContext
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
