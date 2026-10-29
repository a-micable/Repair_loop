def moving_average(x, window):
    out=[]
    for i in range(len(x)):
        chunk=x[max(0,i-window+1):i+1]
        out.append(sum(chunk)/len(chunk))
    return out
