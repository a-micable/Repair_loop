def allan_var(x, tau_samples):
    n=len(x)//tau_samples
    if n<2: return 0.0
    means=[sum(x[i*tau_samples:(i+1)*tau_samples])/tau_samples for i in range(n)]
    s=0.0
    for i in range(n-1):
        d=means[i+1]-means[i]
        s+=d*d
    return s/(2*(n-1))
