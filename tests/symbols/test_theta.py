import unittest

from masmod.symbols._theta import theta, Theta


class TestTheta(unittest.TestCase):

    def test_make_theta(self) -> None:
        test_theta = theta()

        self.assertEqual(str(test_theta), "test_theta")

    def test_mu_ref(self) -> None:
        test_theta = theta(0.1)
        self.assertFalse(test_theta.mu_ref)
        test_theta.mu_ref = True
        self.assertTrue(test_theta.mu_ref)