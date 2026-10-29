import math


def voltage_drop(length_m, diameter_mm, current_a, resistivity=1.68e-8):
    A = math.pi * (diameter_mm * 1e-3 / 2.0) ** 2
    r = resistivity * (2.0 * length_m) / A
    return current_a * r
