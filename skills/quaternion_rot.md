---
title: Quaternion rotate vector
tags: quaternion, rotate, robotics, geometry
---

Unit quaternion `q = (w, x, y, z)`, vector `v`.

Efficient form:

```
t = 2 * cross(q_vec, v)
v' = v + w*t + cross(q_vec, t)
```

Identity `(1,0,0,0)` leaves `v` unchanged. 180° about z is `(0,0,0,1)`.
