# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/module/emax/test_emax.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/06/2022 01:21 pm
#
# Last Modified: 12/09/2022 02:13 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
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

        self.data = pd.read_csv(
            pathlib.Path(__file__).parent.joinpath("dataEmax.csv")
        )
        self.data = self.data[self.data["MDV"] == 0].reset_index()
        self.wt = covariate(self.data["WT"])
        self.height = covariate(self.data["HEIGHT"])

    def pred(self, t) -> tuple[Expression, Expression]:

        em = self.theta_em * (self.wt / 50)**0.75 * ff.exp(self.eta_em)
        if self.height > 180:
            if self.wt > 100:
                em = self.theta_em * (self.wt / 50)**0.8 * ff.exp(self.eta_em)
            else:
                em = self.theta_em

        et = self.theta_et50 * ff.exp(self.eta_et50)

        effect = em * t / (et + t)

        ipred = effect

        y = effect * (1 + self.eps)

        return ipred, y


class TestEmaxModel(unittest.TestCase):

    def test_parse(self) -> None:
        model = EmaxModel()

        with open(
            pathlib.Path(__file__).parent.joinpath("emax_refined.py"),
            mode="w",
            encoding="utf-8"
        ) as f:
            f.write(f"#type: ignore\n{model.refined}")

        with open(
            pathlib.Path(__file__).parent.joinpath("emax.cc"),
            mode="w",
            encoding="utf-8"
        ) as f:
            f.write(model.translated)
