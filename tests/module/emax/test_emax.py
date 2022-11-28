import unittest

import pathlib
import pandas as pd

from masmod.symbols import theta, omega, sigma
from masmod.module import PredRoutine
from masmod.functional import exp


class EmaxModel(PredRoutine):

    def __init__(self) -> None:
        super().__init__()
        self.theta_em = theta(150, bounds=(30, None))
        self.theta_et50 = theta(0.5, bounds=(0.01, None))

        self.eta_em = omega(0.09)
        self.eta_et50 = omega(0.09)

        self.eps = sigma(0.09)

        self.data = pd.read_csv(pathlib.Path(__file__).parent.joinpath("dataEmax.csv"))
        self.data = self.data[self.data["MDV"] == 0]

    def pred(self, t) -> None:
        em = self.theta_em * exp(self.eta_em)
        et = self.theta_et50 * exp(self.eta_et50)

        effect = (em * t) / (et + t)

        self.ipred = effect

        self.y = effect * (1 + self.eps)


class TestEmaxModel(unittest.TestCase):

    def test_parse(self) -> None:
        model = EmaxModel()
