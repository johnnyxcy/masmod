# import ast
# import typing
# import sympy
# from masmod.symbols._variable import SymVar
# from masmod.symbols import ExprContext, ConstContext, GlobalContext

# class AutoDiffNodeTransformer(ast.NodeTransformer):

#     def __init__(self, expr_context: ExprContext, const_context: ConstContext, global_context: GlobalContext) -> None:
#         self._var_context = expr_context

#         self._const_context = const_context
#         self._global_context = global_context

#         self._self_context = expr_context + const_context
#         self._locals: typing.Dict[str, typing.Any] = {
#             "self": self._self_context
#         }

#     def do_partial_derivative(self, expr: sympy.Expr, var_name_prefix: str) -> typing.List[ast.Assign]:
#         partial_deriv_assignments: typing.List[ast.Assign] = []
#         for var in self._var_context.values():
#             if isinstance(var, SymVar):
#                 diff_var_name = ast.Name(id=f"{var_name_prefix}_wrt_{var.name}")
#                 partial_deriv = expr.diff(var)
#                 partial_deriv_code = sympy.pycode(partial_deriv)
#                 if not isinstance(partial_deriv_code, str):
#                     raise ValueError()
#                 partial_deriv_assignments.append(
#                     ast.Assign(targets=(diff_var_name,), value=ast.parse(partial_deriv_code, mode="eval"))
#                 )
#         return partial_deriv_assignments

#     def visit_Assign(self, node: ast.Assign) -> typing.Any:
#         lhs = node.targets
#         rhs = node.value

#         rhs_expr = eval(ast.unparse(rhs), self._global_context.as_dict(), self._locals)

#         # deal with diff
#         diffs: typing.List[ast.Assign] = []
#         if len(lhs) == 1:
#             token = lhs[0]
#             if isinstance(token, ast.Name):
#                 self._locals[token.id] = rhs_expr
#                 if isinstance(rhs_expr, sympy.Expr):
#                     diffs.extend(self.do_partial_derivative(expr=rhs_expr, var_name_prefix=token.id))

#             elif isinstance(token, ast.Attribute):
#                 if isinstance(token.value, ast.Name):
#                     if token.value.id == "self":
#                         setattr(self._locals["self"], token.attr, rhs_expr)
#                         if isinstance(rhs_expr, sympy.Expr):
#                             diffs.extend(
#                                 self.do_partial_derivative(
#                                     expr=rhs_expr, var_name_prefix=f"{token.value.id}_{token.attr}"
#                                 )
#                             )

#                     else:
#                         raise NotImplementedError()
#                 else:
#                     raise NotImplementedError()
#             else:
#                 raise NotImplementedError()
#         else:
#             raise NotImplementedError()

#         return [node, *diffs]

# class PredAutoDiffGenerator:

#     def __init__(
#         self, source_code: str, expr_context: ExprContext, const_context: ConstContext, global_context: GlobalContext
#     ) -> None:
#         self._source_code = source_code
#         self._expr_context = expr_context
#         self._const_context = const_context
#         self._global_context = global_context

#         parse_code_body = ast.parse(self._source_code).body
#         if len(parse_code_body) != 1:
#             raise ValueError("Class Def 只能有一个")
#         _cls_def_ast = parse_code_body[0]
#         if not isinstance(_cls_def_ast, ast.ClassDef):
#             raise TypeError("source_code 不属于 Class Def 类型")
#         self._cls_def_ast: ast.ClassDef = _cls_def_ast

#     def gen(self) -> str:
#         for part in self._cls_def_ast.body:
#             # 如果是名为 "pred" 的函数
#             if isinstance(part, ast.FunctionDef) and part.name == "pred":
#                 self._cls_def_ast = AutoDiffNodeTransformer(
#                     expr_context=self._expr_context,
#                     const_context=self._const_context,
#                     global_context=self._global_context
#                 ).visit(part)
#                 # self._cls_def_ast = ast.fix_missing_locations(self._cls_def_ast)
#                 # AutoDiffNodeTransformer(expr_context=self._expr_context, const_context=self._const_context).visit(part)
#         return ast.unparse(self._cls_def_ast)
