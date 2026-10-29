---
title: Tone SNR from periodogram
tags: snr, fft, dsp, periodogram
---

For a single real tone in noise:

1. remove mean
2. compute DFT magnitudes / power on bins `1 .. N/2-1`
3. signal ≈ peak bin (+/- 1 for leakage)
4. noise ≈ median of remaining bins × count of those bins
5. SNR_dB = 10*log10(sig/noise)

Don't include DC in the noise floor.
