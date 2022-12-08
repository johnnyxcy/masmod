def func(t):
    if t > 180:
        v1 = 120
        v = t - 180
    elif t > 100:
        v = 100
    else:
        v2 = -1
        v = t + 180

    return v


assert func(181) == 1
assert func(150) == 100
assert func(0) == 180
