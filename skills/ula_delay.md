---
title: ULA geometric delay
tags: array, beamforming, ula, delay, acoustics
---

Uniform linear array on x-axis, spacing `d`. Plane wave from angle `theta` measured from broadside (0 = normal).

Path difference to sensor `i` (relative to sensor 0):

`delta_x = i * d * sin(theta)`

Time delay to align:

`tau_i = delta_x / c`

Sensor 0 delay is 0. Watch degrees vs radians.
