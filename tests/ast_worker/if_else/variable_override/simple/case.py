# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/variable_override/simple/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/07/2022 03:14 pm
#
# Last Modified: 12/08/2022 05:49 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    v = 1
    if t > 180:
        if t > 190:
            v = 2
        else:
            v = -1

    elif t > 100:
        v1 = 3

    return v


assert func(191) == 2
assert func(181) == -1
assert func(171) == 1
assert func(0) == 1
assert func(101) == 1
