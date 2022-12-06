# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/module/warfarin/test_warfarin.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/05/2022 02:51 pm
#
# Last Modified: 12/06/2022 04:32 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
import unittest
from masmod.module import *
from masmod.symbols import *
from masmod.functional import *

import pandas as pd
import pathlib


class Warfarin(Module):

    def __init__(self) -> None:
        super().__init__()
        self.theta_V = theta(7.81)
        self.theta_Cl = theta(0.134)
        self.theta_ka = theta(0.571)
        self.theta_alag = theta(0.823)

        self.eta_Cl = omega(0.049)
        self.eta_V = omega(0.0802)
        self.eta_ka = omega(0.047)
        self.eta_alag = omega(0.156)

        self.eps_prop = sigma(0.0104)
        self.eps_add = sigma(0.554)

        data = pd.read_csv(pathlib.Path(__file__).parent.joinpath("warfarin.csv"))
        self.data = data[data['DVID'] == 1]
        self.dose = covariate(self.data["DOSE"])

    def pred(self, t: float) -> tuple[Expression, Expression]:
        alag = self.theta_alag * exp(self.eta_alag)
        cl = self.theta_Cl * exp(self.eta_Cl)
        v = self.theta_V * exp(self.eta_V)
        ka = self.theta_ka * exp(self.eta_ka)
        k = cl / v

        if alag > t:
            ipred = 0
        else:
            ipred = self.dose / v * ka / (ka - k) * (exp(-k * (t - alag)) - exp(-ka * (t - alag)))

        y = ipred * (1 + self.eps_prop) + self.eps_add

        return ipred, y


class TestWarfarinModel(unittest.TestCase):

    def test_parse(self) -> None:
        model = Warfarin()

        with open(".tmp/war.cc", mode="w", encoding="utf-8") as f:
            f.write(model.translated)
