def func(t):
    __bool_1 = t > 10
    __bool_2 = t > 5
    __bool_3 = t < 0
    __bool_4 = __bool_2
    __bool_5 = __bool_3
    __bool_6 = __bool_5
    __else__bool_6__v = 0
    __bool_6__v = 0
    __bool_4__v = 0
    __bool_1__v = 0
    if __bool_1:
        __bool_4 = t > 20
        __bool_5 = t > 15
        __bool_6 = __bool_5
        __else__bool_6__v = 0
        __bool_6__v = 0
        __bool_4__v = 0
        if __bool_4:
            __bool_4__v = 20
        elif __bool_6:
            __bool_6__v = 15
            v0 = -1
        else:
            __else__bool_6__v = 10
        __bool_1__v = __bool_4 * __bool_4__v + (1 - __bool_4) * __bool_6 * __bool_6__v + (1 - __bool_4) * (1 - __bool_6) * __else__bool_6__v
    elif __bool_4:
        __bool_6 = t > 6
        __else__bool_6__v = 0
        __bool_6__v = 0
        if __bool_6:
            v2 = -999
            __bool_6__v = 6
        else:
            v0 = 999
            __else__bool_6__v = 5
        __bool_4__v = __bool_6 * __bool_6__v + (1 - __bool_6) * __else__bool_6__v
    elif __bool_6:
        __bool_6__v = -1
    else:
        __else__bool_6__v = 0
    v = __bool_1 * __bool_1__v + (1 - __bool_1) * __bool_4 * __bool_4__v + (1 - __bool_1) * (1 - __bool_4) * __bool_6 * __bool_6__v + (1 - __bool_1) * (1 - __bool_4) * (1 - __bool_6) * __else__bool_6__v
    __bool_7 = t > 10
    __bool_8 = t < 0
    __bool_9 = __bool_8
    __else__bool_9__p = 0
    __bool_9__p = 0
    __bool_7__p = 0
    if __bool_7:
        __bool_7__p = 0
    elif __bool_9:
        __bool_9__p = -1
    else:
        __else__bool_9__p = 1
    p = __bool_7 * __bool_7__p + (1 - __bool_7) * __bool_9 * __bool_9__p + (1 - __bool_7) * (1 - __bool_9) * __else__bool_9__p
    return (v, p)
assert func(11) == (10, 0)
assert func(16) == (15, 0)
assert func(21) == (20, 0)
assert func(6) == (5, 1)
assert func(8) == (6, 1)
assert func(-999) == (-1, -1)
assert func(3) == (0, 1)