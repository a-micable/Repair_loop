import math


def beta_from_points(r1, t1_c, r2, t2_c):
    T1 = t1_c + 273.15
    T2 = t2_c + 273.15
    return math.log(r1 / r2) / (1.0 / T1 - 1.0 / T2)
