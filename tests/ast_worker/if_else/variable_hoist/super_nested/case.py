# _*_ coding: utf-8 _*_
############################################################
# File: masmod/tests/ast_worker/if_else/variable_hoist/super_nested/case.py
#
# Author: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# File Created: 12/08/2022 03:38 pm
#
# Last Modified: 12/08/2022 03:39 pm
#
# Modified By: Chongyi Xu <johnny.xcy1997@outlook.com>
#
# Copyright (c) 2022 MaS Dev Team
############################################################
def func(t):
    if t > 10:
        if t > 20:
            if t > 30:
                if t > 40:
                    v = 1
                else:
                    v = 2
            else:
                v = 3
        else:
            v = 4
    else:
        v = 5

    return v


assert func(41) == 1
assert func(31) == 2
assert func(21) == 3
assert func(11) == 4
assert func(1) == 5