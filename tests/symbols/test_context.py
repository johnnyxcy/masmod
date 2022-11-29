import unittest

from masmod.symbols._context import VarContext


class TestContext(unittest.TestCase):

    def test_setitem(self) -> None:
        context = VarContext[int]()
        context["some_int"] = 1
        self.assertEqual(context.some_int, 1)

        def expect_type_error() -> None:
            context["some_string"] = "123"

        self.assertRaises(TypeError, expect_type_error)

    def test_two_context(self) -> None:
        int_context = VarContext[int]()
        float_context = VarContext[float]()

        int_context["some_int"] = 1

        self.assertEqual(int_context.some_int, 1)

        def expect_attribute_error() -> None:
            print(float_context.some_int)

        self.assertRaises(AttributeError, expect_attribute_error)

    def test_copy(self) -> None:
        context_a = VarContext[int]()
        context_a["some_int"] = 1
        self.assertEqual(context_a.some_int, 1)

        context_b = context_a.copy()
        self.assertEqual(context_b.some_int, 1)
        context_b["another_int"] = 2
        self.assertEqual(context_b.another_int, 2)

        def expect_attribute_error() -> None:
            print(context_a.another_int)

        self.assertRaises(AttributeError, expect_attribute_error)

    def test_add_context(self) -> None:
        int_context = VarContext[int]()
        float_context = VarContext[float]()

        int_context["some_int"] = 1
        float_context["some_float"] = 1.1
        self.assertEqual(int_context.some_int, 1)
        self.assertEqual(float_context.some_float, 1.1)

        def expect_int_context_attribute_error() -> None:
            print(int_context.some_float)

        self.assertRaises(AttributeError, expect_int_context_attribute_error)

        def expect_float_context_attribute_error() -> None:
            print(float_context.some_int)

        self.assertRaises(AttributeError, expect_float_context_attribute_error)

        mixed = int_context + float_context

        self.assertEqual(mixed.some_int, 1)
        self.assertEqual(mixed.some_float, 1.1)

        def expect_mixed_context_type_error() -> None:
            mixed["some_str"] = "string_value"

        self.assertRaises(TypeError, expect_mixed_context_type_error)

        mixed["another_int"] = 123

        def expect_int_context_attribute_error1() -> None:
            print(int_context.another_int)

        self.assertRaises(AttributeError, expect_int_context_attribute_error1)

        def expect_float_context_attribute_error1() -> None:
            print(float_context.another_int)

        self.assertRaises(AttributeError, expect_float_context_attribute_error1)
