import ast
import typing
import sympy
from ..symbols._variable import SymVar
from ..symbols import ExprContext, ConstContext, GlobalContext


class AutoDiffNodeTransformer(ast.NodeTransformer):

    def __init__(self, expr_context: ExprContext, const_context: ConstContext, global_context: GlobalContext) -> None:
        self._var_context = expr_context

        self._const_context = const_context
        self._global_context = global_context

        self._self_context = expr_context + const_context
        self._locals: typing.Dict[str, typing.Any] = {
            "self": self._self_context
        }

    def _append_partial_derivative(self, expr: sympy.Expr, var_name_prefix: str) -> typing.List[ast.Assign]:
        partial_deriv_assignments: typing.List[ast.Assign] = []
        for var in self._var_context.values():
            if isinstance(var, SymVar):
                diff_var_name = ast.Name(id=f"{var_name_prefix}_wrt_{var.name}")
                partial_deriv = expr.diff(var)
                partial_deriv_code = sympy.pycode(partial_deriv, fully_qualified_modules=False)
                if not isinstance(partial_deriv_code, str):
                    raise ValueError()
                partial_deriv_assignments.append(
                    ast.Assign(targets=(diff_var_name,), value=ast.parse(partial_deriv_code, mode="eval"))
                )
        return partial_deriv_assignments

    def visit_Assign(self, node: ast.Assign) -> typing.Any:
        lhs = node.targets
        rhs = node.value

        rhs_expr = eval(ast.unparse(rhs), self._global_context.as_dict(), self._locals)

        # deal with diff
        diffs: typing.List[ast.Assign] = []
        if len(lhs) == 1:
            token = lhs[0]
            if isinstance(token, ast.Name):
                self._locals[token.id] = rhs_expr
                if isinstance(rhs_expr, sympy.Expr):
                    diffs.extend(self._append_partial_derivative(expr=rhs_expr, var_name_prefix=token.id))

            elif isinstance(token, ast.Attribute):
                if isinstance(token.value, ast.Name):
                    if token.value.id == "self":
                        setattr(self._locals["self"], token.attr, rhs_expr)
                        if isinstance(rhs_expr, sympy.Expr):
                            diffs.extend(
                                self._append_partial_derivative(
                                    expr=rhs_expr, var_name_prefix=f"{token.value.id}_{token.attr}"
                                )
                            )

                    else:
                        raise NotImplementedError()
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        return [node, *diffs]
