import ast
import typing
import sympy

from ...symbols import ExprContext, ConstContext, GlobalContext


class AutoDiffNodeTransformer(ast.NodeTransformer):

    def __init__(self, expr_context: ExprContext, const_context: ConstContext, global_context: GlobalContext) -> None:
        self._var_context = expr_context

        self._const_context = const_context
        self._global_context = global_context

        self._locals = expr_context + const_context

    def visit_Call(self, node: ast.Call) -> typing.Any:
        print(node)
        return node

    def visit_Assign(self, node: ast.Assign) -> typing.Any:
        lhs = node.targets
        rhs = node.value

        rhs_expr = eval(ast.unparse(rhs), self._global_context.as_dict(), {"self": self._locals})
        if isinstance(rhs_expr, sympy.Expr):
            for var in self._var_context.values():
                print(rhs_expr.diff(var))
        else:
            pass

        print(lhs)
        print(rhs)


class PredAutoDiffGenerator:

    def __init__(
        self, source_code: str, expr_context: ExprContext, const_context: ConstContext, global_context: GlobalContext
    ) -> None:
        self._source_code = source_code
        self._expr_context = expr_context
        self._const_context = const_context
        self._global_context = global_context

        parse_code_body = ast.parse(self._source_code).body
        if len(parse_code_body) != 1:
            raise ValueError("Class Def 只能有一个")
        _cls_def_ast = parse_code_body[0]
        if not isinstance(_cls_def_ast, ast.ClassDef):
            raise TypeError("source_code 不属于 Class Def 类型")
        self._cls_def_ast: ast.ClassDef = _cls_def_ast

    def gen(self) -> str:
        for part in self._cls_def_ast.body:
            # 如果是名为 "pred" 的函数
            if isinstance(part, ast.FunctionDef) and part.name == "pred":
                AutoDiffNodeTransformer(
                    expr_context=self._expr_context,
                    const_context=self._const_context,
                    global_context=self._global_context
                ).visit(part)
                # AutoDiffNodeTransformer(expr_context=self._expr_context, const_context=self._const_context).visit(part)
        return ast.unparse(self._cls_def_ast)
