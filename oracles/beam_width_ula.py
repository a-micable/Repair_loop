import math

def half_power_beamwidth_deg(n, d_over_lambda):
    return math.degrees(0.886/(n*d_over_lambda))
