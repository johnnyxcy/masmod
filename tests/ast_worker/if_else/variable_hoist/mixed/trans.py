def func(t):
    t_greater_15 = t > 15
    __bool_1 = t > 10
    __bool_2 = t > 5
    __bool_3 = t < 0
    __bool_4 = 0
    if __bool_1:
        __bool_4 = t > 20
        __elset_greater_15__v = 0
        t_greater_15__v = 0
        __bool_4__v = 0
        if __bool_4:
            __bool_4__v = 20
        elif t_greater_15:
            t_greater_15__v = 15
            v0 = -1
        else:
            __elset_greater_15__v = 10
        v = __bool_4 * __bool_4__v + (1 - __bool_4) * t_greater_15 * t_greater_15__v + (1 - __bool_4) * (1 - t_greater_15) * __elset_greater_15__v
    elif __bool_2:
        __bool_4 = t > 6
        if __bool_4:
            v2 = -999
            v = 6
        else:
            v0 = 999
            v = 5
    elif __bool_3:
        v = -1
    else:
        v = 0
    __bool_5 = t > 10
    __bool_6 = t < 0
    __else__bool_6__p = 0
    __bool_6__p = 0
    __bool_5__p = 0
    if __bool_5:
        __bool_5__p = 0
    elif __bool_6:
        __bool_6__p = -1
    else:
        __else__bool_6__p = 1
    p = __bool_5 * __bool_5__p + (1 - __bool_5) * __bool_6 * __bool_6__p + (1 - __bool_5) * (1 - __bool_6) * __else__bool_6__p
    return (v, p)
assert func(11) == (10, 0)
assert func(16) == (15, 0)
assert func(21) == (20, 0)
assert func(6) == (5, 1)
assert func(8) == (6, 1)
assert func(-999) == (-1, -1)
assert func(3) == (0, 1)