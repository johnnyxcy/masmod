import unittest
import numpy as np
from masmod.symbols.variable import Variable


class TestVariable(unittest.TestCase):

    def test_new(self) -> None:
        var = Variable(name="var", init_value=0.1, bounds=(0, 1))
        self.assertIsInstance(var, Variable)
        self.assertEqual(str(var), "var")
        self.assertEqual(var.init_value, 0.1)
        self.assertEqual(var.bounds, (0, 1))

    def test_rename(self) -> None:
        var = Variable("var")
        self.assertTrue(str(var) == "var")

        var.name = "some_name"
        self.assertEqual(str(var), "some_name")

    def test_change_init_value(self) -> None:
        var = Variable("var")
        self.assertEqual(var.init_value, 0)

        var.init_value = 1.0
        self.assertEqual(var.init_value, 1.0)

    def test_change_bounds(self) -> None:
        var = Variable("var")
        self.assertEqual(var.bounds, (-np.inf, np.inf))

        var.bounds = (0, 1)
        self.assertEqual(var.bounds, (0, 1))