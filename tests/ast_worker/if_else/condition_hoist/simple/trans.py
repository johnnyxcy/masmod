def func(t):
    v = 1
    __bool_1 = t > 180
    if __bool_1:
        v = 2
    return v
assert func(181) == 2
assert func(0) == 1