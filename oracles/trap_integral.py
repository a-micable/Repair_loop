def trapz(y, dx):
    if len(y)<2:
        return 0.0
    s=y[0]+y[-1]
    s+=2*sum(y[1:-1])
    return s*dx/2.0
