---
title: Discrete PID on Euler plant
tags: pid, control, discrete, ee
---

Plant example: `dx/dt = -x + u`, Euler: `x <- x + dt*(-x + u)`.

Positional PID:

`u = kp*e + ki*integ - kd*(dx/dt)`

with `e = setpoint - x`, integrate `e*dt`, derivative often on measurement to avoid setpoint kicks. Clip `u` to actuator limits.
