---
title: Classical RK4 step
tags: ode, rk4, numerics
---

For y' = f(t,y):

```
k1 = f(t, y)
k2 = f(t+h/2, y+h*k1/2)
k3 = f(t+h/2, y+h*k2/2)
k4 = f(t+h, y+h*k3)
y_next = y + h*(k1 + 2*k2 + 2*k3 + k4)/6
```
