import math

def refract_deg(n1, n2, theta1_deg):
    s=n1/n2*math.sin(math.radians(theta1_deg))
    if abs(s)>1:
        return None
    return math.degrees(math.asin(s))
