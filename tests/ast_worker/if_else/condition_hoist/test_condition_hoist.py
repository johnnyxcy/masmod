# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/condition_hoist/test_condition_hoist.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/07/2022 03:13 pm
#
# Last Modified: 12/08/2022 03:59 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import ast
import pathlib
import unittest
import sympy
from masmod.ast_worker.if_else.condition_hoist import IfElseConditionHoistTransformer
from masmod.symbols import AnyContext


class TestConditionHoist(unittest.TestCase):

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
        transformer = IfElseConditionHoistTransformer(
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

    def test_case_multiple(self) -> None:
        self._do_test_case("multiple")

    def test_case_elif(self) -> None:
        self._do_test_case("elif")

    def test_case_named_condition(self) -> None:
        self._do_test_case("named_condition")
