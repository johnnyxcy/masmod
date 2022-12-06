# _*_ coding: utf-8 _*_
############################################################
# File: masmod/masmod/symbols/_expr.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/05/2022 03:53 pm
#
# Last Modified: 12/06/2022 04:31 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################

import sympy

Expression = sympy.Expr | int | float
