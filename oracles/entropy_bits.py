import math

def entropy_bits(probs):
    h=0.0
    for p in probs:
        if p>0:
            h-=p*math.log2(p)
    return h
