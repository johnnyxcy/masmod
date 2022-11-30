import ast
import typing
import sympy
from masmod.symbols._variable import SymVar
from masmod.symbols import ExprContext, AnyContext
from masmod.translator import ASTSympyTranslator
from masmod.utils.mask_self import mask_self_attr


class AutoDiffNodeTransformer(ast.NodeTransformer):

    def __init__(
        self,
        var_context: ExprContext,
        local_context: AnyContext,
        global_context: AnyContext,
    ) -> None:
        self._var_context = var_context

        self._locals = local_context.as_dict()
        self._globals = global_context.as_dict()

        self._sympy_translator = ASTSympyTranslator(self_context=var_context, local_context=local_context)

        self._partial_deriv_term_names_mapping: typing.Dict[str, typing.List[str]] = {}

    def get_partial_deriv_term_names(self, var_name: str) -> typing.List[str]:
        """获取生成 var_name 对应的 partial derivate 变量名

        Args:
            var_name (str): 尝试获取的 var_name

        Returns:
            typing.List[str]: var_name 对应的 partial derivatives 的变量名
        """
        if var_name not in self._partial_deriv_term_names_mapping.keys():
            raise KeyError("{0} 没有生成对应的 partial derivative".format(var_name))
        return self._partial_deriv_term_names_mapping[var_name]

    def _append_partial_derivative(self, expr: sympy.Expr, var_name_prefix: str) -> typing.List[ast.Assign]:
        partial_deriv_assignments: typing.List[ast.Assign] = []
        for var in self._var_context.values():
            if isinstance(var, SymVar):
                diff_var_name = ast.Name(id=f"{var_name_prefix}_wrt_{var.name}")

                if var_name_prefix not in self._partial_deriv_term_names_mapping.keys():
                    self._partial_deriv_term_names_mapping[var_name_prefix] = [diff_var_name.id]
                else:
                    self._partial_deriv_term_names_mapping[var_name_prefix].append(diff_var_name.id)

                partial_deriv = expr.diff(var)
                ast_expr = self._sympy_translator.translate(partial_deriv)
                partial_deriv_assignments.append(ast.Assign(targets=(diff_var_name,), value=ast_expr))
        return partial_deriv_assignments

    # def visit_If(self, node: ast.If) -> typing.Any:
    #     return node

    def visit_Assign(self, node: ast.Assign) -> typing.Any:
        lhs = node.targets
        rhs = node.value
        rhs_expr = eval(ast.unparse(rhs), self._globals, self._locals)

        # deal with diff
        diffs: typing.List[ast.Assign] = []
        if len(lhs) == 1:
            token = lhs[0]
            if isinstance(token, ast.Name):
                self._locals[token.id] = rhs_expr
                if isinstance(rhs_expr, sympy.Expr):
                    diffs.extend(self._append_partial_derivative(expr=rhs_expr, var_name_prefix=f"__{token.id}"))

            elif isinstance(token, ast.Attribute):
                if isinstance(token.value, ast.Name):
                    if token.value.id == "self":
                        setattr(self._locals["self"], token.attr, rhs_expr)
                        if isinstance(rhs_expr, sympy.Expr):
                            diffs.extend(
                                self._append_partial_derivative(
                                    expr=rhs_expr, var_name_prefix=mask_self_attr(token.attr)
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
