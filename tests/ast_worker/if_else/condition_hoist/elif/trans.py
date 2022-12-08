def func(t):
    v = 1
    __bool_1 = t == 0
    __bool_2 = t > 180
    if __bool_1:
        v = 2
    elif __bool_2:
        v = 3
    else:
        v = 4
    return v
assert func(0) == 2
assert func(181) == 3
assert func(-1) == 4