def func(t):
    v = 1

    if t > 180:
        v1 = 120
    else:
        v2 = -1

    return v


assert func(1) == 1
assert func(181) == 1