import ast
import typing
import copy
from ...symbols import ExprContext, ConstContext, VarContext


class AutoDiffNodeTransformer(ast.NodeTransformer):

    def __init__(self, expr_context: ExprContext, const_context: ConstContext) -> None:
        self._var_context = expr_context
        self._const_context = const_context

        self._locals = expr_context + const_context

    def visit_Call(self, node: ast.Call) -> typing.Any:
        print(node)
        return node

    def visit_Assign(self, node: ast.Assign) -> typing.Any:
        lhs = node.targets
        rhs = node.value

        result = eval(ast.unparse(rhs), {}, {"self": self._locals})
        print(result)

        print(lhs)
        print(rhs)


class PredAutoDiffGenerator:

    def __init__(self, cls_def_code: str, expr_context: ExprContext, const_context: ConstContext) -> None:
        self._cls_def_code = cls_def_code
        self._expr_context = expr_context
        self._const_context = const_context

        parse_code_body = ast.parse(self._cls_def_code).body
        if len(parse_code_body) != 1:
            raise ValueError("Class Def 只能有一个")
        _cls_def_ast = parse_code_body[0]
        if not isinstance(_cls_def_ast, ast.ClassDef):
            raise TypeError("TODO:")
        self._cls_def_ast: ast.ClassDef = _cls_def_ast

    def gen(self) -> str:
        for part in self._cls_def_ast.body:
            # 如果是名为 "pred" 的函数
            if isinstance(part, ast.FunctionDef) and part.name == "pred":
                print('1')
                AutoDiffNodeTransformer(expr_context=self._expr_context, const_context=self._const_context).visit(part)
        return ast.unparse(self._cls_def_ast)
