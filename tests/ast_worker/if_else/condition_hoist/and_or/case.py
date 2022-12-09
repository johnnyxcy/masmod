# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/condition_hoist/and_or/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/09/2022 02:33 pm
#
# Last Modified: 12/09/2022 02:34 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    v = 1

    if t == 0 or t == -1:
        v = 2

    elif t > 180:
        v = 3

    else:
        v = 4

    return v


assert func(0) == 2
assert func(181) == 3
assert func(-1) == 2