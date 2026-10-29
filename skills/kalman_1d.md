---
title: Scalar Kalman update
tags: kalman, estimation, filter
---

```
K = P / (P + R)
x ← x + K*(z - x)
P ← (1 - K)*P
```
