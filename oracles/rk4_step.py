def rk4_step(f, t, y, h):
    k1=f(t,y)
    k2=f(t+0.5*h, y+0.5*h*k1)
    k3=f(t+0.5*h, y+0.5*h*k2)
    k4=f(t+h, y+h*k3)
    return y+(h/6.0)*(k1+2*k2+2*k3+k4)
