# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/symbols/test_variable.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/25/2022 08:44 am
#
# Last Modified: 12/06/2022 04:33 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import unittest
import numpy as np
from masmod.symbols._variable import SymVar


class TestVariable(unittest.TestCase):

    def test_new(self) -> None:
        var = SymVar(name="var", init_value=0.1, bounds=(0, 1))
        self.assertIsInstance(var, SymVar)
        self.assertEqual(str(var), "var")
        self.assertEqual(var.init_value, 0.1)
        self.assertEqual(var.bounds, (0, 1))

    def test_rename(self) -> None:
        var = SymVar("var")
        self.assertTrue(str(var) == "var")

        var.name = "some_name"
        self.assertEqual(str(var), "some_name")

    def test_change_init_value(self) -> None:
        var = SymVar("var")
        self.assertEqual(var.init_value, 0)

        var.init_value = 1.0
        self.assertEqual(var.init_value, 1.0)

    def test_change_bounds(self) -> None:
        var = SymVar("var")
        self.assertEqual(var.bounds, (-np.inf, np.inf))

        var.bounds = (0, 1)
        self.assertEqual(var.bounds, (0, 1))