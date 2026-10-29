import math

def goertzel_power(y, k):
    n=len(y)
    w=2*math.pi*k/n
    coeff=2*math.cos(w)
    q0=q1=q2=0.0
    for v in y:
        q0=v+coeff*q1-q2
        q2,q1=q1,q0
    return q1*q1 + q2*q2 - coeff*q1*q2
