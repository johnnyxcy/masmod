import unittest
import numpy as np
from masmod.symbols.sigma import SigmaBlock, Eps, sigma


class TestSigma(unittest.TestCase):

    def test_single_eta(self) -> None:
        eps1 = sigma(init_sigma=1)

        self.assertIsInstance(eps1, Eps)
        self.assertEqual(str(eps1), "eps1")
        self.assertEqual(eps1.init_value, 1)
        self.assertEqual(eps1.bounds, (-np.inf, np.inf))
        np.testing.assert_array_equal(eps1.sigma.init_values, np.array([[1]]))
        self.assertEqual(eps1.sigma.init_values.shape, (1, 1))
        np.testing.assert_array_equal(eps1.sigma.lower_bounds, np.array([[-np.inf]]))
        np.testing.assert_array_equal(eps1.sigma.upper_bounds, np.array([[np.inf]]))

    def test_single_eta_with_args(self) -> None:
        eps2 = sigma(init_sigma=2., bounds=(None, 10), fixed=True)
        self.assertIsInstance(eps2, Eps)
        self.assertEqual(str(eps2), "eps2")
        self.assertEqual(eps2.init_value, 2)
        self.assertEqual(eps2.fixed, True)
        self.assertEqual(eps2.bounds, (-np.inf, 10))
        np.testing.assert_array_equal(eps2.sigma.init_values, np.array([[2]]))
        self.assertEqual(eps2.sigma.init_values.shape, (1, 1))
        np.testing.assert_array_equal(eps2.sigma.lower_bounds, np.array([[-np.inf]]))
        np.testing.assert_array_equal(eps2.sigma.upper_bounds, np.array([[10]]))

    def test_single_eta_invalid(self) -> None:

        # 如果只提供了一个 init_sigma 却指定了两个 eps，就报错
        def expect_value_error() -> None:
            eps1, eps2 = sigma(init_sigma=2)  # type: ignore

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_full_sigma(self) -> None:
        eps1, eps2 = sigma(init_sigma=[[1.1, 0], [0, 2.2]], bounds=[(0, 10), None])

        self.assertIsInstance(eps1, Eps)
        self.assertIsInstance(eps2, Eps)

        self.assertEqual(str(eps1), "eps1")
        self.assertEqual(str(eps2), "eps2")
        self.assertEqual(eps1.init_value, 1.1)
        self.assertEqual(eps2.init_value, 2.2)

        self.assertEqual(eps1.bounds, (0, 10))
        self.assertEqual(eps2.bounds, (-np.inf, np.inf))

        # eps1 和 eps2 应该公用了同一个 Sigma
        self.assertEqual(id(eps1.sigma), id(eps2.sigma))

        np.testing.assert_array_equal(eps1.sigma.init_values, np.array([[1.1, 0], [0, 2.2]]))
        self.assertEqual(eps1.sigma.init_values.shape, (2, 2))
        np.testing.assert_array_equal(eps1.sigma.lower_bounds, np.array([[0, 0], [0, -np.inf]]))
        np.testing.assert_array_equal(eps1.sigma.upper_bounds, np.array([[10, 0], [0, np.inf]]))

    def test_multiple_eta_full_sigma_n_eta_mismatched(self) -> None:

        def expect_value_error() -> None:
            eps1, eps2, eta_non_exists = sigma(init_sigma=[[1.1, 0], [0, 2.2]], bounds=[(0, 10), None])

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_full_sigma_invalid(self) -> None:

        def expect_value_error() -> None:
            eps1 = sigma(init_sigma=[[1.1, 0], [0, 2.2]], bounds=[(0, 10), None])

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_full_sigma_not_symmetric(self) -> None:

        def expect_value_error() -> None:
            eps1, eps2 = sigma(init_sigma=[[1.1, 1], [0, 2.2]], bounds=[(0, 10), None])

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_block_sigma(self) -> None:
        # yapf: disable
        eps1, eps2 = sigma(init_sigma=SigmaBlock(
            tril=[
                1.1,
                0, 2.2
            ],
            dimension=2
        ))
        # yapf: enable

        self.assertIsInstance(eps1, Eps)
        self.assertIsInstance(eps2, Eps)
        self.assertEqual(str(eps1), "eps1")
        self.assertEqual(str(eps2), "eps2")

        self.assertEqual(eps1.init_value, 1.1)
        self.assertEqual(eps2.init_value, 2.2)
        self.assertEqual(eps1.bounds, (-np.inf, np.inf))
        self.assertEqual(eps2.bounds, (-np.inf, np.inf))

        # eps1 和 eps2 应该公用了同一个 Sigma
        self.assertEqual(id(eps1.sigma), id(eps2.sigma))

        np.testing.assert_array_equal(eps1.sigma.init_values, np.array([[1.1, 0], [0, 2.2]]))
        self.assertEqual(eps1.sigma.init_values.shape, (2, 2))
        np.testing.assert_array_equal(eps1.sigma.lower_bounds, np.array([[-np.inf, 0], [0, -np.inf]]))
        np.testing.assert_array_equal(eps1.sigma.upper_bounds, np.array([[np.inf, 0], [0, np.inf]]))

    def test_multiple_eta_block_sigma_dimension_mismatched(self) -> None:

        def expect_value_error() -> None:
            # yapf: disable
            eps1, eps2 = sigma(init_sigma=SigmaBlock(
                tril=[
                    1.1,
                    0, 2.2
                ],
                dimension=3
            ))
            # yapf: enable

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_bounds_mismatched(self) -> None:

        def expect_value_error_block() -> None:
            # yapf: disable
            eps1, eps2 = sigma(init_sigma=SigmaBlock(
                tril=[
                    1.1,
                    0, 2.2
                ],
                dimension=2,
            ), bounds=[None, None, None, None])
            # yapf: enable

        self.assertRaises(ValueError, expect_value_error_block)

        def expect_value_error_full() -> None:
            eps1, eps2 = sigma(init_sigma=[[1.1, 0], [0, 2.2]], bounds=[None])

        self.assertRaises(ValueError, expect_value_error_full)
