# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/variable_hoist/test_variable_hoist.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 09:21 am
#
# Last Modified: 12/08/2022 03:46 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
import pathlib
import sympy
import unittest

from masmod.ast_worker.if_else.variable_hoist import IfElseVariableHoistTransformer
from masmod.symbols import AnyContext


class TestVariableHoist(unittest.TestCase):

    def _do_test_case(self, case_name: str) -> None:
        with open(
            pathlib.Path(__file__).parent.joinpath(f"{case_name}/case.py"),
            mode="r",
            encoding="utf-8"
        ) as f:
            source_code = f.read()

        context = AnyContext()
        context["t"] = sympy.Symbol("t")
        node = ast.parse(source_code)
        transformer = IfElseVariableHoistTransformer(
            source_code=source_code,
            global_context=context,
            local_context=context
        )
        transformer.visit(node)

        transformed = ast.unparse(node)
        with open(
            pathlib.Path(__file__).parent.joinpath(f"{case_name}/trans.py"),
            mode="w",
            encoding="utf-8"
        ) as f:
            f.write(transformed)

        exec(transformed)

    def test_case_simple(self) -> None:
        self._do_test_case("simple")

    def test_case_elif(self) -> None:
        self._do_test_case("elif")

    def test_case_nested(self) -> None:
        self._do_test_case("nested")

    def test_case_super_nested(self) -> None:
        self._do_test_case("super_nested")

    def test_case_nohoist(self) -> None:
        self._do_test_case("nohoist")

    def test_case_mixed(self) -> None:
        self._do_test_case("mixed")
