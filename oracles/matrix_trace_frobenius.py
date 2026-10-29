import math


def trace_and_frobenius(A):
    n = len(A)
    tr = sum(A[i][i] for i in range(n))
    s = 0.0
    for row in A:
        for v in row:
            s += v * v
    return tr, math.sqrt(s)
