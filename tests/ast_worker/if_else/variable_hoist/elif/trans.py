def func(t):
    __bool_1 = t > 180
    __bool_2 = t > 100
    __else__bool_2__v = 0
    __bool_2__v = 0
    __bool_1__v = 0
    if __bool_1:
        v1 = 120
        __bool_1__v = t - 180
    elif __bool_2:
        __bool_2__v = 100
    else:
        v2 = -1
        __else__bool_2__v = t + 180
    v = __bool_1 * __bool_1__v + (1 - __bool_1) * __bool_2 * __bool_2__v + (1 - __bool_1) * (1 - __bool_2) * __else__bool_2__v
    return v
assert func(181) == 1
assert func(150) == 100
assert func(0) == 180