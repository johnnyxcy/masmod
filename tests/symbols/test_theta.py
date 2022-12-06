# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/symbols/test_theta.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 11/25/2022 08:59 am
#
# Last Modified: 12/06/2022 04:33 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import unittest

from masmod.symbols._theta import theta


class TestTheta(unittest.TestCase):

    def test_make_theta(self) -> None:
        test_theta = theta()

        self.assertEqual(str(test_theta), "test_theta")

    def test_mu_ref(self) -> None:
        test_theta = theta(0.1)
        self.assertFalse(test_theta.mu_ref)
        test_theta.mu_ref = True
        self.assertTrue(test_theta.mu_ref)