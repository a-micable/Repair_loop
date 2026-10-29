import cmath, math

def peak_frequency_hz(y, fs):
    n=len(y)
    best_k, best_m = 1, -1.0
    for k in range(1, n//2):
        acc=0j
        for i,v in enumerate(y):
            acc += v*cmath.exp(-2j*math.pi*k*i/n)
        m=abs(acc)
        if m>best_m:
            best_m, best_k = m, k
    return best_k*fs/n
