import cmath
import math


def estimate_snr_db(y):
    n = len(y)
    mu = sum(y) / n
    x = [v - mu for v in y]
    # power spectrum via DFT (one-sided)
    ps = []
    for k in range(n // 2):
        acc = 0j
        for i, v in enumerate(x):
            acc += v * cmath.exp(-2j * math.pi * k * i / n)
        # unnormalized power contribution
        ps.append((abs(acc) ** 2) / n)

    peak_i = max(range(1, len(ps)), key=lambda i: ps[i])  # skip DC
    # gather a tight peak neighborhood
    neigh = {peak_i}
    if peak_i - 1 >= 1:
        neigh.add(peak_i - 1)
    if peak_i + 1 < len(ps):
        neigh.add(peak_i + 1)

    sig = sum(ps[i] for i in neigh)
    noise_bins = [ps[i] for i in range(1, len(ps)) if i not in neigh]
    # robust noise floor
    noise_bins.sort()
    med = noise_bins[len(noise_bins) // 2] if noise_bins else 1e-18
    noise = med * max(len(noise_bins), 1)
    return 10 * math.log10(max(sig, 1e-18) / max(noise, 1e-18))
