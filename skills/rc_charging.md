---
title: RC step response
tags: rc, circuit, tau, exponential, ee
---

Charging from 0 toward Vinf:

`v(t) = Vinf * (1 - exp(-t / tau))`

Rearrange for tau when you have a mid-point sample:

`tau = -t / ln(1 - v/Vinf)`

Estimate Vinf from late samples (max or mean of the tail). Average tau over several mid-curve points; throw out points too close to 0 or Vinf where the log blows up.
