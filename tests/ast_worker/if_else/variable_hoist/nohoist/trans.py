def func(t):
    v = 1
    __bool_1 = t > 180
    if __bool_1:
        v1 = 120
    else:
        v2 = -1
    return v
assert func(1) == 1
assert func(181) == 1