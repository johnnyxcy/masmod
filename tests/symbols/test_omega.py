# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/symbols/test_omega.py
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
from masmod.symbols._omega import OmegaBlock, Eta, omega


class TestOmega(unittest.TestCase):

    def test_single_eta(self) -> None:
        eta1 = omega(init_omega=1)

        self.assertIsInstance(eta1, Eta)
        self.assertEqual(str(eta1), "eta1")
        self.assertEqual(eta1.init_value, 1)
        self.assertEqual(eta1.bounds, (-np.inf, np.inf))
        np.testing.assert_array_equal(eta1.omega.init_values, np.array([[1]]))
        self.assertEqual(eta1.omega.init_values.shape, (1, 1))
        np.testing.assert_array_equal(eta1.omega.lower_bounds, np.array([[-np.inf]]))
        np.testing.assert_array_equal(eta1.omega.upper_bounds, np.array([[np.inf]]))

    def test_single_eta_with_args(self) -> None:
        eta2 = omega(init_omega=2., bounds=(None, 10), fixed=True)
        self.assertIsInstance(eta2, Eta)
        self.assertEqual(str(eta2), "eta2")
        self.assertEqual(eta2.init_value, 2)
        self.assertEqual(eta2.fixed, True)
        self.assertEqual(eta2.bounds, (-np.inf, 10))
        np.testing.assert_array_equal(eta2.omega.init_values, np.array([[2]]))
        self.assertEqual(eta2.omega.init_values.shape, (1, 1))
        np.testing.assert_array_equal(eta2.omega.lower_bounds, np.array([[-np.inf]]))
        np.testing.assert_array_equal(eta2.omega.upper_bounds, np.array([[10]]))

    def test_single_eta_invalid(self) -> None:

        # 如果只提供了一个 init_omega 却指定了两个 eta，就报错
        def expect_value_error() -> None:
            eta1, eta2 = omega(init_omega=2)  # type: ignore

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_full_omega(self) -> None:
        eta1, eta2 = omega(init_omega=[[1.1, 0], [0, 2.2]], bounds=[(0, 10), None])

        self.assertIsInstance(eta1, Eta)
        self.assertIsInstance(eta2, Eta)

        self.assertEqual(str(eta1), "eta1")
        self.assertEqual(str(eta2), "eta2")
        self.assertEqual(eta1.init_value, 1.1)
        self.assertEqual(eta2.init_value, 2.2)

        self.assertEqual(eta1.bounds, (0, 10))
        self.assertEqual(eta2.bounds, (-np.inf, np.inf))

        # eta1 和 eta2 应该公用了同一个 Omega
        self.assertEqual(id(eta1.omega), id(eta2.omega))

        np.testing.assert_array_equal(eta1.omega.init_values, np.array([[1.1, 0], [0, 2.2]]))
        self.assertEqual(eta1.omega.init_values.shape, (2, 2))
        np.testing.assert_array_equal(eta1.omega.lower_bounds, np.array([[0, 0], [0, -np.inf]]))
        np.testing.assert_array_equal(eta1.omega.upper_bounds, np.array([[10, 0], [0, np.inf]]))

    def test_multiple_eta_full_omega_n_eta_mismatched(self) -> None:

        def expect_value_error() -> None:
            eta1, eta2, eta_non_exists = omega(init_omega=[[1.1, 0], [0, 2.2]], bounds=[(0, 10), None])

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_full_omega_invalid(self) -> None:

        def expect_value_error() -> None:
            eta1 = omega(init_omega=[[1.1, 0], [0, 2.2]], bounds=[(0, 10), None])

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_full_omega_not_symmetric(self) -> None:

        def expect_value_error() -> None:
            eta1, eta2 = omega(init_omega=[[1.1, 1], [0, 2.2]], bounds=[(0, 10), None])

        self.assertRaises(ValueError, expect_value_error)

    def test_multiple_eta_block_omega(self) -> None:
        # yapf: disable
        eta1, eta2 = omega(init_omega=OmegaBlock(
            tril=[
                1.1,
                0, 2.2
            ],
            dimension=2
        ))
        # yapf: enable

        self.assertIsInstance(eta1, Eta)
        self.assertIsInstance(eta2, Eta)
        self.assertEqual(str(eta1), "eta1")
        self.assertEqual(str(eta2), "eta2")

        self.assertEqual(eta1.init_value, 1.1)
        self.assertEqual(eta2.init_value, 2.2)
        self.assertEqual(eta1.bounds, (-np.inf, np.inf))
        self.assertEqual(eta2.bounds, (-np.inf, np.inf))

        # eta1 和 eta2 应该公用了同一个 Omega
        self.assertEqual(id(eta1.omega), id(eta2.omega))

        np.testing.assert_array_equal(eta1.omega.init_values, np.array([[1.1, 0], [0, 2.2]]))
        self.assertEqual(eta1.omega.init_values.shape, (2, 2))
        np.testing.assert_array_equal(eta1.omega.lower_bounds, np.array([[-np.inf, 0], [0, -np.inf]]))
        np.testing.assert_array_equal(eta1.omega.upper_bounds, np.array([[np.inf, 0], [0, np.inf]]))

    def test_multiple_eta_block_omega_dimension_mismatched(self) -> None:

        def expect_value_error() -> None:
            # yapf: disable
            eta1, eta2 = omega(init_omega=OmegaBlock(
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
            eta1, eta2 = omega(init_omega=OmegaBlock(
                tril=[
                    1.1,
                    0, 2.2
                ],
                dimension=2,
            ), bounds=[None, None, None, None])
            # yapf: enable

        self.assertRaises(ValueError, expect_value_error_block)

        def expect_value_error_full() -> None:
            eta1, eta2 = omega(init_omega=[[1.1, 0], [0, 2.2]], bounds=[None])

        self.assertRaises(ValueError, expect_value_error_full)
