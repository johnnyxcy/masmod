# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/condition_hoist/multiple/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/07/2022 03:14 pm
#
# Last Modified: 12/08/2022 01:26 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    v = 1

    if t == 0:
        v = 2

    if t > 180:
        v = 3

    return v


assert func(1) == 1
assert func(0) == 2
assert func(181) == 3