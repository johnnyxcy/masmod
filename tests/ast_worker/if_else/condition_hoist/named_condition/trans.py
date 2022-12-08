def func(t):
    cond = t == 5
    __bool_1 = t > 10
    if __bool_1:
        v = 10
    elif cond:
        v = 5
    else:
        v = 0
    return v
assert func(11) == 10
assert func(5) == 5
assert func(6) == 0
assert func(1) == 0