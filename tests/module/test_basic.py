import unittest
from masmod.module._base import BaseModule


class TestBaseModule(unittest.TestCase):

    def test_no_data(self) -> None:

        class NoDataModel(BaseModule):

            def __init__(self) -> None:
                super().__init__()
                self.val = 10

        def expect_value_error() -> None:
            model = NoDataModel()

        self.assertRaises(ValueError, expect_value_error)

    def test_data_type_error(self) -> None:

        class InvalidDataTypeModel(BaseModule):

            def __init__(self) -> None:
                super().__init__()
                self.data = 100

        def expect_type_error() -> None:
            model = InvalidDataTypeModel()

        self.assertRaises(TypeError, expect_type_error)
