import math

def zipf_slope(freqs):
    ys=[math.log(f) for f in freqs]
    xs=[math.log(i+1) for i in range(len(freqs))]
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den=sum((x-mx)**2 for x in xs) or 1.0
    return num/den
