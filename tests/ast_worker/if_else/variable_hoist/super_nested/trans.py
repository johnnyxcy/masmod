def func(t):
    __bool_1 = t > 10
    __bool_2 = 0
    __bool_3 = 0
    __bool_4 = 0
    if __bool_1:
        __bool_2 = t > 20
        __bool_3 = 0
        __bool_4 = 0
        if __bool_2:
            __bool_3 = t > 30
            __bool_4 = 0
            if __bool_3:
                __bool_4 = t > 40
                __else__bool_4__v = 0
                __bool_4__v = 0
                if __bool_4:
                    __bool_4__v = 1
                else:
                    __else__bool_4__v = 2
                v = __bool_4 * __bool_4__v + (1 - __bool_4) * __else__bool_4__v
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