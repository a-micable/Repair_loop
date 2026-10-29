def req(series, parallels):
    total=sum(series)
    for group in parallels:
        if not group:
            continue
        inv=sum(1.0/r for r in group)
        total += 1.0/inv
    return total
