import math

def db_power(p, p_ref):
    return 10*math.log10(p/p_ref)

def db_amplitude(a, a_ref):
    return 20*math.log10(a/a_ref)
