import cmath
import math


def estimate_frequencies(y, fs):
    # lightweight DFT peak picker — good enough for well-separated tones
    n = len(y)
    mags = []
    for k in range(1, n // 2):
        acc = 0j
        for i, v in enumerate(y):
            acc += v * cmath.exp(-2j * math.pi * k * i / n)
        mags.append((abs(acc), k * fs / n))
    mags.sort(reverse=True)
    # take peaks with separation
    peaks = []
    for mag, f in mags:
        if mag < mags[0][0] * 0.15:
            break
        if all(abs(f - p) > 1.5 for p in peaks):
            peaks.append(f)
        if len(peaks) >= 3:
            break
    return sorted(peaks)
