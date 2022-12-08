# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/variable_hoist/mixed/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 03:42 pm
#
# Last Modified: 12/08/2022 04:09 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    t_greater_15 = t > 15
    if t > 10:
        if t > 20:
            v = 20
        elif t_greater_15:
            v = 15
            v0 = -1
        else:
            v = 10
    elif t > 5:
        if t > 6:
            v2 = -999
            v = 6
        else:
            v0 = 999
            v = 5
    elif t < 0:
        v = -1
    else:
        v = 0

    if t > 10:
        p = 0
    elif t < 0:
        p = -1
    else:
        p = 1

    return v, p


assert func(11) == (10, 0)
assert func(16) == (15, 0)
assert func(21) == (20, 0)
assert func(6) == (5, 1)
assert func(8) == (6, 1)
assert func(-999) == (-1, -1)
assert func(3) == (0, 1)