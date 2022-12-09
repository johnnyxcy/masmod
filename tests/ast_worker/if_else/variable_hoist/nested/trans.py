def func(t):
    __bool_1 = t > 180
    __bool_2 = 0
    if __bool_1:
        v1 = 120
        __bool_2 = v1 > 100
        __else__bool_2__v = 0
        __bool_2__v = 0
        if __bool_2:
            v2 = 222
            __bool_2__v = t - 100
        else:
            __else__bool_2__v = 100 - t
        v = __bool_2 * __bool_2__v + (1 - __bool_2) * __else__bool_2__v
    else:
        v2 = -1
        v = t + 180
    return v
assert func(181) == 81
assert func(100) == 280