import unittest

import pathlib
import pandas as pd

from masmod.symbols import theta, omega, sigma, covariate
from masmod.module import PredModule
import masmod.functional as ff


class EmaxModel(PredModule):

    def __init__(self) -> None:
        super().__init__()
        self.theta_em = theta(150, bounds=(30, None))
        self.theta_et50 = theta(0.5, bounds=(0.01, None))

        self.eta_em = omega(0.09)
        self.eta_et50 = omega(0.09)

        self.eps = sigma(0.09)

        self.data = pd.read_csv(pathlib.Path(__file__).parent.joinpath("dataEmax.csv"))
        self.data = self.data[self.data["MDV"] == 0].reset_index()
        self.mdv = covariate(self.data["MDV"])

    def pred(self, t):
        # em = self.theta_em * ff.exp(self.eta_em) * self.mdv
        # et = self.theta_et50 * ff.exp(self.eta_et50)

        if self.mdv == 1:
            effect = 0
        else:
            effect = 1

        self.ipred = effect

        self.y = effect * (1 + self.eps)


class TestEmaxModel(unittest.TestCase):

    def test_parse(self) -> None:
        model = EmaxModel()

        def expect_not_implemented_error_accessing_ipred() -> None:
            print(model.ipred)

        self.assertRaises(NotImplementedError, expect_not_implemented_error_accessing_ipred)

        def expect_not_implemented_error_accessing_y() -> None:
            print(model.y)

        self.assertRaises(NotImplementedError, expect_not_implemented_error_accessing_y)

        with open(".tmp/out.cc", mode="w", encoding="utf-8") as f:
            f.write(model.translated)
