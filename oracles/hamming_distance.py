def hamming(a, b):
    if len(a)!=len(b):
        raise ValueError('length')
    return sum(int(x)!=int(y) for x,y in zip(a,b))
