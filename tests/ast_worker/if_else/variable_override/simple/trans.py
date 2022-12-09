def func(t):
    v = 1
    __bool_1 = t > 180
    __bool_2 = t > 100
    __bool_1__v = 0
    if __bool_1:
        __bool_3 = t > 190
        __else__bool_3__v = 0
        __bool_3__v = 0
        if __bool_3:
            __bool_3__v = 2
        else:
            __else__bool_3__v = -1
        __bool_1__v = __bool_3 * __bool_3__v + (1 - __bool_3) * __else__bool_3__v
    elif __bool_2:
        v1 = 3
    v = __bool_1 * __bool_1__v + (1 - __bool_1) * __bool_2 * v + (1 - __bool_1) * (1 - __bool_2) * v
    return v
assert func(191) == 2
assert func(181) == -1
assert func(171) == 1
assert func(0) == 1
assert func(101) == 1