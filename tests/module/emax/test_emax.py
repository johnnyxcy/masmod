import unittest

import pathlib
import pandas as pd

from masmod.symbols import theta, omega, sigma, covariate, Expression
from masmod.module import Module
import masmod.functional as ff


class EmaxModel(Module):

    def __init__(self) -> None:
        super().__init__()
        self.theta_em = theta(150, bounds=(30, None))
        self.theta_et50 = theta(0.5, bounds=(0.01, None))

        self.eta_em = omega(0.09)
        self.eta_et50 = omega(0.09)

        self.eps = sigma(0.09)

        self.data = pd.read_csv(pathlib.Path(__file__).parent.joinpath("dataEmax.csv"))
        self.data = self.data[self.data["MDV"] == 0].reset_index()
        self.wt = covariate(self.data["WT"])
        self.height = covariate(self.data["HEIGHT"])

    def pred(self, t) -> tuple[Expression, Expression]:

        if self.height > 180:
            em = self.theta_em * (self.wt / 50)**0.75 * ff.exp(self.eta_em)
        else:
            em = self.theta_em * (1 + self.eta_em)

        et = self.theta_et50 * ff.exp(self.eta_et50)

        effect = em * t / (et + t)

        ipred = effect

        y = effect * (1 + self.eps)

        return ipred, y


class TestEmaxModel(unittest.TestCase):

    def test_parse(self) -> None:
        model = EmaxModel()

        with open(".tmp/emax.cc", mode="w", encoding="utf-8") as f:
            f.write(model.translated)
