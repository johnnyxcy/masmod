# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/condition_hoist/named_condition/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 03:58 pm
#
# Last Modified: 12/08/2022 03:59 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    cond = t == 5
    if t > 10:
        v = 10
    elif cond:
        v = 5
    else:
        v = 0

    return v


assert func(11) == 10
assert func(5) == 5
assert func(6) == 0
assert func(1) == 0
