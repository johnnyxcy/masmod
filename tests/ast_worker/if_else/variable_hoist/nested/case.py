# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/variable_hoist/nested/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 11:18 am
#
# Last Modified: 12/08/2022 04:53 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    if t > 180:
        v1 = 120
        if v1 > 100:
            v2 = 222
            v = t - 100
        else:
            v = 100 - t
    else:
        v2 = -1
        v = t + 180
    return v


assert func(181) == 81
assert func(100) == 280
