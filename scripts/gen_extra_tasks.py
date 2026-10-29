#!/usr/bin/env python3
"""Generate additional LabForge tasks + oracles (idempotent)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
ORACLES = ROOT / "oracles"

SPEC: list[dict] = [
    {
        "id": "gcd_euclid",
        "title": "Euclidean GCD",
        "difficulty": "easy",
        "tags": ["math", "algorithms"],
        "prompt": "Implement `gcd(a, b)` returning the non-negative GCD. Stdlib only.",
        "public_tests_hint": "- gcd(0,0)==0\n- matches math.gcd on public pairs",
        "test_source": "import math\nimport solution\n\ndef run():\n    assert solution.gcd(0,0)==0\n    for a,b in [(12,18),(100,35),(-14,21),(0,9)]:\n        assert solution.gcd(a,b)==math.gcd(a,b)\n",
        "oracle": "def gcd(a, b):\n    a, b = abs(a), abs(b)\n    while b:\n        a, b = b, a % b\n    return a\n",
    },
    {
        "id": "hamming_distance",
        "title": "Hamming distance of bitstrings",
        "difficulty": "easy",
        "tags": ["info-theory", "dsp"],
        "prompt": "Implement `hamming(a, b)` for equal-length 0/1 strings (or equal-length int lists of 0/1). Return int distance.",
        "public_tests_hint": "- identical → 0\n- single flip → 1",
        "test_source": "import solution\n\ndef run():\n    assert solution.hamming('000','000')==0\n    assert solution.hamming('1010','0010')==1\n    assert solution.hamming([1,1,0],[0,1,1])==2\n",
        "oracle": "def hamming(a, b):\n    if len(a)!=len(b):\n        raise ValueError('length')\n    return sum(int(x)!=int(y) for x,y in zip(a,b))\n",
    },
    {
        "id": "moving_average",
        "title": "Simple moving average",
        "difficulty": "easy",
        "tags": ["dsp", "stats"],
        "prompt": "Implement `moving_average(x, window)` returning a list of means for each index using the last `window` samples (or fewer at start).",
        "public_tests_hint": "- window=1 identity\n- matches hand calculation",
        "test_source": "import solution\n\ndef run():\n    x=[1,2,3,4,5]\n    assert solution.moving_average(x,1)==[1.0,2.0,3.0,4.0,5.0]\n    out=solution.moving_average(x,3)\n    assert abs(out[0]-1)<1e-12 and abs(out[2]-2)<1e-12 and abs(out[4]-4)<1e-12\n",
        "oracle": "def moving_average(x, window):\n    out=[]\n    for i in range(len(x)):\n        chunk=x[max(0,i-window+1):i+1]\n        out.append(sum(chunk)/len(chunk))\n    return out\n",
    },
    {
        "id": "trap_integral",
        "title": "Trapezoidal integration",
        "difficulty": "easy",
        "tags": ["numerics", "math"],
        "prompt": "Implement `trapz(y, dx)` — composite trapezoid rule on equally spaced samples with step dx. Return float.",
        "public_tests_hint": "- integrates y=1 → length*dx\n- integrates linear ramp accurately",
        "test_source": "import solution\n\ndef run():\n    y=[1,1,1,1]\n    assert abs(solution.trapz(y,0.5)-1.5)<1e-12\n    y2=[0,1,2,3]\n    assert abs(solution.trapz(y2,1.0)-4.5)<1e-12\n",
        "oracle": "def trapz(y, dx):\n    if len(y)<2:\n        return 0.0\n    s=y[0]+y[-1]\n    s+=2*sum(y[1:-1])\n    return s*dx/2.0\n",
    },
    {
        "id": "softmax",
        "title": "Numerically stable softmax",
        "difficulty": "medium",
        "tags": ["ml", "numerics"],
        "prompt": "Implement `softmax(logits)` returning a probability list that sums to 1. Use max-subtraction for stability. Stdlib math.",
        "public_tests_hint": "- sums to 1\n- argmax preserved\n- handles large logits",
        "test_source": "import math\nimport solution\n\ndef run():\n    p=solution.softmax([1.0,2.0,3.0])\n    assert abs(sum(p)-1)<1e-9\n    assert p.index(max(p))==2\n    p2=solution.softmax([1000.0,1000.0,1000.0])\n    assert all(math.isfinite(x) for x in p2) and abs(sum(p2)-1)<1e-9\n",
        "oracle": "import math\n\ndef softmax(logits):\n    m=max(logits)\n    ex=[math.exp(v-m) for v in logits]\n    s=sum(ex) or 1.0\n    return [e/s for e in ex]\n",
    },
    {
        "id": "entropy_bits",
        "title": "Shannon entropy in bits",
        "difficulty": "medium",
        "tags": ["info-theory", "stats"],
        "prompt": "Implement `entropy_bits(probs)` for a discrete distribution (list of probs summing ~1). Ignore zero bins. Return bits (log2).",
        "public_tests_hint": "- fair coin → 1 bit\n- deterministic → 0",
        "test_source": "import math\nimport solution\n\ndef run():\n    assert abs(solution.entropy_bits([0.5,0.5])-1.0)<1e-9\n    assert abs(solution.entropy_bits([1.0,0.0]))<1e-9\n    h=solution.entropy_bits([0.25]*4)\n    assert abs(h-2.0)<1e-9\n",
        "oracle": "import math\n\ndef entropy_bits(probs):\n    h=0.0\n    for p in probs:\n        if p>0:\n            h-=p*math.log2(p)\n    return h\n",
    },
    {
        "id": "impedance_series_parallel",
        "title": "Series/parallel resistor network",
        "difficulty": "easy",
        "tags": ["ee", "circuits"],
        "prompt": "Implement `req(series, parallels)` where `series` is a list of ohms in series, `parallels` is a list of parallel groups (each a list of ohms). Total = series sum + sum of parallel equivalents. Empty parallel groups ignored.",
        "public_tests_hint": "- series-only works\n- two 10Ω parallel → 5Ω",
        "test_source": "import solution\n\ndef run():\n    assert abs(solution.req([2,3],[])-5)<1e-12\n    assert abs(solution.req([],[ [10,10] ])-5)<1e-12\n    assert abs(solution.req([1],[ [4,4,2] ])-2)<1e-12\n",
        "oracle": "def req(series, parallels):\n    total=sum(series)\n    for group in parallels:\n        if not group:\n            continue\n        inv=sum(1.0/r for r in group)\n        total += 1.0/inv\n    return total\n",
    },
    {
        "id": "decibel_ratio",
        "title": "Power and amplitude dB",
        "difficulty": "easy",
        "tags": ["ee", "dsp"],
        "prompt": "Implement `db_power(p, p_ref)` and `db_amplitude(a, a_ref)` returning 10 log10 and 20 log10 ratios respectively.",
        "public_tests_hint": "- 2x power → ~3.01 dB\n- 2x amplitude → ~6.02 dB",
        "test_source": "import math\nimport solution\n\ndef run():\n    assert abs(solution.db_power(2.0,1.0)-10*math.log10(2))<1e-12\n    assert abs(solution.db_amplitude(2.0,1.0)-20*math.log10(2))<1e-12\n",
        "oracle": "import math\n\ndef db_power(p, p_ref):\n    return 10*math.log10(p/p_ref)\n\ndef db_amplitude(a, a_ref):\n    return 20*math.log10(a/a_ref)\n",
    },
    {
        "id": "levenshtein",
        "title": "Levenshtein edit distance",
        "difficulty": "medium",
        "tags": ["algorithms", "nlp"],
        "prompt": "Implement `edit_distance(a, b)` classic Levenshtein distance (insert/delete/substitute cost 1).",
        "public_tests_hint": "- identical 0\n- kitten/sitting → 3",
        "test_source": "import solution\n\ndef run():\n    assert solution.edit_distance('a','a')==0\n    assert solution.edit_distance('kitten','sitting')==3\n    assert solution.edit_distance('','abc')==3\n",
        "oracle": "def edit_distance(a, b):\n    n,m=len(a),len(b)\n    dp=[[0]*(m+1) for _ in range(n+1)]\n    for i in range(n+1):\n        dp[i][0]=i\n    for j in range(m+1):\n        dp[0][j]=j\n    for i in range(1,n+1):\n        for j in range(1,m+1):\n            cost=0 if a[i-1]==b[j-1] else 1\n            dp[i][j]=min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)\n    return dp[n][m]\n",
    },
    {
        "id": "newton_sqrt",
        "title": "Newton square root",
        "difficulty": "medium",
        "tags": ["numerics", "math"],
        "prompt": "Implement `newton_sqrt(x, iters=20)` for x>=0 using Newton iteration starting from x or 1. Return float.",
        "public_tests_hint": "- sqrt(9)≈3\n- sqrt(2) within 1e-10 of math.sqrt",
        "test_source": "import math\nimport solution\n\ndef run():\n    assert abs(solution.newton_sqrt(9)-3)<1e-10\n    assert abs(solution.newton_sqrt(2)-math.sqrt(2))<1e-10\n    assert solution.newton_sqrt(0)==0\n",
        "oracle": "def newton_sqrt(x, iters=20):\n    if x==0:\n        return 0.0\n    y=x if x>1 else 1.0\n    for _ in range(iters):\n        y=0.5*(y+x/y)\n    return y\n",
    },
    {
        "id": "rk4_step",
        "title": "RK4 ODE step",
        "difficulty": "hard",
        "tags": ["numerics", "ode", "physics"],
        "prompt": "Implement `rk4_step(f, t, y, h)` one classical RK4 step for scalar ODE y'=f(t,y). `f` is a callable. Return y_{n+1}.",
        "public_tests_hint": "- exact on y'=y over one small step within tolerance\n- order sanity vs Euler",
        "test_source": "import math\nimport solution\n\ndef run():\n    f=lambda t,y: y\n    y0=1.0\n    h=0.01\n    y1=solution.rk4_step(f,0.0,y0,h)\n    expect=math.exp(h)\n    assert abs(y1-expect)<1e-8\n",
        "oracle": "def rk4_step(f, t, y, h):\n    k1=f(t,y)\n    k2=f(t+0.5*h, y+0.5*h*k1)\n    k3=f(t+0.5*h, y+0.5*h*k2)\n    k4=f(t+h, y+h*k3)\n    return y+(h/6.0)*(k1+2*k2+2*k3+k4)\n",
    },
    {
        "id": "biquad_lowpass_coeff",
        "title": "RBJ lowpass biquad coefficients",
        "difficulty": "hard",
        "tags": ["dsp", "audio", "ee"],
        "prompt": "Implement `lowpass_biquad(fc, fs, Q=1/math.sqrt(2))` returning (b0,b1,b2,a0,a1,a2) for the Audio EQ Cookbook lowpass. Use stdlib math. a0 should be 1 after normalization (divide all by a0).",
        "public_tests_hint": "- a0==1\n- coefficients finite\n- matches cookbook within 1e-9 for a public fc/fs",
        "test_source": "import math\nimport solution\n\ndef _ref(fc, fs, Q=1/math.sqrt(2)):\n    w0=2*math.pi*fc/fs\n    alpha=math.sin(w0)/(2*Q)\n    cosw=math.cos(w0)\n    b0=(1-cosw)/2\n    b1=1-cosw\n    b2=(1-cosw)/2\n    a0=1+alpha\n    a1=-2*cosw\n    a2=1-alpha\n    return tuple(v/a0 for v in (b0,b1,b2,a0,a1,a2))\n\ndef run():\n    got=solution.lowpass_biquad(1000.0,48000.0)\n    ref=_ref(1000.0,48000.0)\n    assert abs(got[3]-1.0)<1e-12\n    assert all(abs(a-b)<1e-9 for a,b in zip(got,ref))\n",
        "oracle": "import math\n\ndef lowpass_biquad(fc, fs, Q=None):\n    if Q is None:\n        Q=1/math.sqrt(2)\n    w0=2*math.pi*fc/fs\n    alpha=math.sin(w0)/(2*Q)\n    cosw=math.cos(w0)\n    b0=(1-cosw)/2\n    b1=1-cosw\n    b2=(1-cosw)/2\n    a0=1+alpha\n    a1=-2*cosw\n    a2=1-alpha\n    return tuple(v/a0 for v in (b0,b1,b2,a0,a1,a2))\n",
    },
    {
        "id": "kalman_1d_update",
        "title": "1D Kalman filter update",
        "difficulty": "hard",
        "tags": ["estimation", "control", "ee"],
        "prompt": "Implement `kalman_update(x, P, z, R)` for scalar state: compute Kalman gain, updated mean and variance. Return (x_new, P_new).",
        "public_tests_hint": "- with tiny R, x moves toward z\n- P decreases",
        "test_source": "import solution\n\ndef run():\n    x,P=0.0,1.0\n    xn,Pn=solution.kalman_update(x,P,10.0,0.01)\n    assert xn>5 and Pn<P\n    x2,P2=solution.kalman_update(0.0,1.0,10.0,1e6)\n    assert abs(x2)<1.0\n",
        "oracle": "def kalman_update(x, P, z, R):\n    K=P/(P+R)\n    x_new=x+K*(z-x)\n    P_new=(1-K)*P\n    return x_new, P_new\n",
    },
    {
        "id": "beam_width_ula",
        "title": "ULA approximate beamwidth",
        "difficulty": "medium",
        "tags": ["arrays", "ee", "rf"],
        "prompt": "Implement `half_power_beamwidth_deg(n, d_over_lambda)` approximate broadside HPBW in degrees: 0.886 * (lambda/(N*d)) in radians converted to degrees (use math). `d_over_lambda` is d/λ.",
        "public_tests_hint": "- larger N → narrower beam\n- matches formula within 1e-9",
        "test_source": "import math\nimport solution\n\ndef run():\n    bw=solution.half_power_beamwidth_deg(10,0.5)\n    expect=math.degrees(0.886/(10*0.5))\n    assert abs(bw-expect)<1e-9\n    assert solution.half_power_beamwidth_deg(20,0.5)<bw\n",
        "oracle": "import math\n\ndef half_power_beamwidth_deg(n, d_over_lambda):\n    return math.degrees(0.886/(n*d_over_lambda))\n",
    },
    {
        "id": "blackbody_peak",
        "title": "Wien displacement peak wavelength",
        "difficulty": "easy",
        "tags": ["physics", "thermal"],
        "prompt": "Implement `wien_peak_um(T_kelvin)` returning λ_max in micrometers using b=2897.771955 μm·K.",
        "public_tests_hint": "- 5800K near ~0.5 μm\n- cooler → longer wavelength",
        "test_source": "import solution\n\ndef run():\n    lam=solution.wien_peak_um(5800.0)\n    assert abs(lam-2897.771955/5800.0)<1e-9\n    assert solution.wien_peak_um(3000.0)>lam\n",
        "oracle": "def wien_peak_um(T_kelvin):\n    return 2897.771955/T_kelvin\n",
    },
    {
        "id": "radioactive_decay",
        "title": "Radioactive decay remaining fraction",
        "difficulty": "easy",
        "tags": ["physics", "nuclear"],
        "prompt": "Implement `remaining_fraction(halflife, t)` = 0.5**(t/halflife).",
        "public_tests_hint": "- one half-life → 0.5\n- two → 0.25",
        "test_source": "import solution\n\ndef run():\n    assert abs(solution.remaining_fraction(10,10)-0.5)<1e-12\n    assert abs(solution.remaining_fraction(5,10)-0.25)<1e-12\n",
        "oracle": "def remaining_fraction(halflife, t):\n    return 0.5 ** (t/halflife)\n",
    },
    {
        "id": "snell_refract",
        "title": "Snell's law refraction angle",
        "difficulty": "medium",
        "tags": ["physics", "optics"],
        "prompt": "Implement `refract_deg(n1, n2, theta1_deg)` returning theta2 in degrees via Snell's law. If TIR, return None.",
        "public_tests_hint": "- n1=n2 → same angle\n- TIR returns None",
        "test_source": "import math\nimport solution\n\ndef run():\n    assert abs(solution.refract_deg(1.0,1.0,30.0)-30.0)<1e-9\n    th=solution.refract_deg(1.0,1.5,30.0)\n    expect=math.degrees(math.asin(1.0/1.5*math.sin(math.radians(30))))\n    assert abs(th-expect)<1e-9\n    assert solution.refract_deg(1.5,1.0,50.0) is None\n",
        "oracle": "import math\n\ndef refract_deg(n1, n2, theta1_deg):\n    s=n1/n2*math.sin(math.radians(theta1_deg))\n    if abs(s)>1:\n        return None\n    return math.degrees(math.asin(s))\n",
    },
    {
        "id": "pid_aw_step",
        "title": "PID with anti-windup clamp",
        "difficulty": "hard",
        "tags": ["control", "ee"],
        "prompt": "Implement `pid_aw(kp, ki, kd, setpoint, n_steps, dt=0.05, umin=-1, umax=1)` like simulate_pid but freeze integral when u would saturate (conditional integration). Plant dx/dt=-x+u. Return x trajectory list.",
        "public_tests_hint": "- length n_steps\n- stays finite\n- with high ki still settles near setpoint better than windup-prone case on public params",
        "test_source": "import math\nimport solution\n\ndef run():\n    traj=solution.pid_aw(3.0, 8.0, 0.0, 1.0, 200, dt=0.02, umin=-1, umax=1)\n    assert len(traj)==200\n    assert all(math.isfinite(x) for x in traj)\n    assert abs(traj[-1]-1.0)<0.25\n",
        "oracle": "def pid_aw(kp, ki, kd, setpoint, n_steps, dt=0.05, umin=-1, umax=1):\n    x=0.0\n    integ=0.0\n    prev_x=0.0\n    out=[]\n    for _ in range(n_steps):\n        e=setpoint-x\n        dx=(x-prev_x)/dt if dt else 0.0\n        u_unsat=kp*e + ki*integ - kd*dx\n        u=max(umin, min(umax, u_unsat))\n        if not ((u>=umax and e>0) or (u<=umin and e<0)):\n            integ += e*dt\n        prev_x=x\n        x=x+dt*(-x+u)\n        out.append(x)\n    return out\n",
    },
    {
        "id": "fft_peak_freq",
        "title": "DFT peak frequency estimate",
        "difficulty": "medium",
        "tags": ["dsp", "fft"],
        "prompt": "Implement `peak_frequency_hz(y, fs)` using a DFT magnitude peak (skip DC). Return Hz. Stdlib cmath/math.",
        "public_tests_hint": "- recovers a clean tone within 1 bin",
        "test_source": "import cmath, math\nimport solution\n\ndef _tone(fs,f,n=256):\n    return [math.sin(2*math.pi*f*i/fs) for i in range(n)]\n\ndef run():\n    fs=128.0\n    y=_tone(fs, 16.0)\n    hat=solution.peak_frequency_hz(y, fs)\n    assert abs(hat-16.0) <= fs/len(y) + 1e-9\n",
        "oracle": "import cmath, math\n\ndef peak_frequency_hz(y, fs):\n    n=len(y)\n    best_k, best_m = 1, -1.0\n    for k in range(1, n//2):\n        acc=0j\n        for i,v in enumerate(y):\n            acc += v*cmath.exp(-2j*math.pi*k*i/n)\n        m=abs(acc)\n        if m>best_m:\n            best_m, best_k = m, k\n    return best_k*fs/n\n",
    },
    {
        "id": "convex_hull_cross",
        "title": "Cross product orientation",
        "difficulty": "easy",
        "tags": ["geometry", "algorithms"],
        "prompt": "Implement `orient(ax,ay,bx,by,cx,cy)` returning sign of cross (B-A)×(C-A): 1 left, -1 right, 0 collinear (use a small epsilon 1e-12).",
        "public_tests_hint": "- known CCW triangle → 1\n- collinear → 0",
        "test_source": "import solution\n\ndef run():\n    assert solution.orient(0,0,1,0,0,1)==1\n    assert solution.orient(0,0,1,0,0,-1)==-1\n    assert solution.orient(0,0,1,0,2,0)==0\n",
        "oracle": "def orient(ax,ay,bx,by,cx,cy):\n    val=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)\n    if abs(val)<1e-12:\n        return 0\n    return 1 if val>0 else -1\n",
    },
]


def main() -> None:
    TASKS.mkdir(exist_ok=True)
    ORACLES.mkdir(exist_ok=True)
    for spec in SPEC:
        oracle = spec.pop("oracle")
        tid = spec["id"]
        (TASKS / f"{tid}.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
        (ORACLES / f"{tid}.py").write_text(oracle, encoding="utf-8")
        print("wrote", tid)
    print("total specs", len(SPEC))


if __name__ == "__main__":
    main()
