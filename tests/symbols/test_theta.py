import unittest

from masmod.symbols._theta import theta, Theta


class TestTheta(unittest.TestCase):

    def test_make_theta(self) -> None:
        test_theta = theta()

        self.assertEqual(str(test_theta), "test_theta")