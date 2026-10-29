def debounce(samples, window):
    out = []
    for i in range(len(samples)):
        chunk = samples[max(0, i - window + 1) : i + 1]
        ones = sum(chunk)
        zeros = len(chunk) - ones
        out.append(1 if ones >= zeros else 0)
    return out
