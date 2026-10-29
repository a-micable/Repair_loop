def newton_sqrt(x, iters=20):
    if x==0:
        return 0.0
    y=x if x>1 else 1.0
    for _ in range(iters):
        y=0.5*(y+x/y)
    return y
