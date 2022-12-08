def func(t):
    v = 1
    __bool_1 = t == 0
    if __bool_1:
        v = 2
    __bool_2 = t > 180
    if __bool_2:
        v = 3
    return v
assert func(1) == 1
assert func(0) == 2
assert func(181) == 3