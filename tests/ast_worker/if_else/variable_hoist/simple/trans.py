def func(t):
    __bool_1 = t > 180
    __else__bool_1__v = 0
    __bool_1__v = 0
    if __bool_1:
        v1 = 120
        __bool_1__v = t - v1
    else:
        v2 = -1
        __else__bool_1__v = t + 180
    v = __bool_1 * __bool_1__v + (1 - __bool_1) * __else__bool_1__v
    return v
assert func(181) == 61
assert func(0) == 180