import math

def lowpass_biquad(fc, fs, Q=None):
    if Q is None:
        Q=1/math.sqrt(2)
    w0=2*math.pi*fc/fs
    alpha=math.sin(w0)/(2*Q)
    cosw=math.cos(w0)
    b0=(1-cosw)/2
    b1=1-cosw
    b2=(1-cosw)/2
    a0=1+alpha
    a1=-2*cosw
    a2=1-alpha
    return tuple(v/a0 for v in (b0,b1,b2,a0,a1,a2))
