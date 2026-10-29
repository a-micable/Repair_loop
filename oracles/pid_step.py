def simulate_pid(kp, ki, kd, setpoint, n_steps, dt=0.05):
    x = 0.0
    integ = 0.0
    prev_x = 0.0
    out = []
    for _ in range(n_steps):
        e = setpoint - x
        integ += e * dt
        dx = (x - prev_x) / dt if dt else 0.0
        u = kp * e + ki * integ - kd * dx
        u = max(-2.0, min(2.0, u))
        prev_x = x
        x = x + dt * (-x + u)
        out.append(x)
    return out
