import math


def fit_rc_tau(t, v):
    vinf = max(v) if v else 1.0
    acc = []
    for ti, vi in zip(t, v):
        if ti <= 0 or not (0.15 * vinf < vi < 0.92 * vinf):
            continue
        r = 1.0 - vi / vinf
        if 0 < r < 1:
            acc.append(-ti / math.log(r))
    return sum(acc) / len(acc) if acc else 0.01
