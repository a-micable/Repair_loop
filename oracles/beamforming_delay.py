import math


def steering_delays(n_sensors, d, c, theta_deg):
    s = math.sin(math.radians(theta_deg))
    return [(i * d * s) / c for i in range(n_sensors)]
