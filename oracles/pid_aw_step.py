def pid_aw(kp, ki, kd, setpoint, n_steps, dt=0.05, umin=-1, umax=1):
    x=0.0
    integ=0.0
    prev_x=0.0
    out=[]
    for _ in range(n_steps):
        e=setpoint-x
        dx=(x-prev_x)/dt if dt else 0.0
        u_unsat=kp*e + ki*integ - kd*dx
        u=max(umin, min(umax, u_unsat))
        if not ((u>=umax and e>0) or (u<=umin and e<0)):
            integ += e*dt
        prev_x=x
        x=x+dt*(-x+u)
        out.append(x)
    return out
