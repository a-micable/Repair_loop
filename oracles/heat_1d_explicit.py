def heat_step(u, alpha, dx, dt):
    r = alpha * dt / (dx * dx)
    out = list(u)
    for i in range(1, len(u) - 1):
        out[i] = u[i] + r * (u[i - 1] - 2 * u[i] + u[i + 1])
    out[0] = u[0]
    out[-1] = u[-1]
    return out
