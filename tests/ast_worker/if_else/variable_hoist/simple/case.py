def func(t):
    if t > 180:
        v1 = 120
        v = t - v1
    else:
        v2 = -1
        v = t + 180

    return v


assert func(181) == 61
assert func(0) == 180
