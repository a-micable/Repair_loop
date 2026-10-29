import math


def projectile_range(v0, angle_deg, g=9.81):
    return (v0 * v0) * math.sin(math.radians(2 * angle_deg)) / g
