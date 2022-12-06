# _*_ coding: utf-8 _*_
"""
File: masmod/masmod/ast_worker/func_return.py

Author: Chongyi Xu <johnny.xcy1997@outlook.com>

File Created: 12/05/2022 04:09 pm

Last Modified: 12/06/2022 04:23 pm

Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>

Copyright (c) 2022 MaS Dev Team
"""
import typing
import ast

from ..utils.rethrow import rethrow, locatable


class FuncReturnVisitor(ast.NodeVisitor):

    def __init__(self, source_code: str) -> None:
        super().__init__()
        self._source_code = source_code
        self._func_def: ast.FunctionDef | None = None
        self._return_expr: ast.Return | None = None

    @property
    def func_def(self) -> ast.FunctionDef:
        if self._func_def is None:
            raise ValueError("没有找到函数")
        return self._func_def

    @property
    def return_expr(self) -> ast.Return:
        if self._return_expr is None:
            rethrow(self._source_code, self.func_def, ValueError("函数体内没有 return"))
        return self._return_expr

    def visit_FunctionDef(self, node: ast.FunctionDef) -> typing.Any:
        self.generic_visit(node)
        if self._func_def is not None:
            rethrow(self._source_code, node, ValueError("函数体内存在 closure"))
        self._func_def = node
        return node

    def visit_Return(self, node: ast.Return) -> typing.Any:
        self.generic_visit(node)
        if self._return_expr is not None:
            rethrow(self._source_code, node, ValueError("函数体内存在多个 return"))
        self._return_expr = node
        return node