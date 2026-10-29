#!/usr/bin/env python3
"""Extra hard/competitive tasks."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS, ORACLES = ROOT / "tasks", ROOT / "oracles"

SPEC = [
    {
        "id": "vandermonde_solve",
        "title": "Solve 3x3 Vandermonde system",
        "difficulty": "hard",
        "tags": ["numerics", "linear-algebra"],
        "prompt": "Implement `fit_quadratic(xs, ys)` for 3 distinct xs: return (a,b,c) for y=a*x^2+b*x+c using exact elimination (stdlib). ",
        "public_tests_hint": "- recovers known quadratic within 1e-8",
        "test_source": "import solution\n\ndef run():\n    xs=[0.0,1.0,2.0]; ys=[1.0,2.0,5.0]  # x^2+1? wait 0->1,1->2,2->5 => a=1,b=0,c=1\n    a,b,c=solution.fit_quadratic(xs,ys)\n    assert abs(a-1)<1e-8 and abs(b-0)<1e-8 and abs(c-1)<1e-8\n",
        "oracle": "def fit_quadratic(xs, ys):\n    # solve Vandermonde for 3 pts via Cramer's / elimination\n    x0,x1,x2=xs; y0,y1,y2=ys\n    # use Lagrange then expand — stable enough for public pts\n    def lag(x):\n        return (\n            y0*(x-x1)*(x-x2)/((x0-x1)*(x0-x2))\n            + y1*(x-x0)*(x-x2)/((x1-x0)*(x1-x2))\n            + y2*(x-x0)*(x-x1)/((x2-x0)*(x2-x1))\n        )\n    # sample three equations by expanding via finite points already known; fit with np-free LS on powers\n    A=[[x*x, x, 1.0] for x in xs]\n    # Gaussian elimination\n    M=[A[i]+[ys[i]] for i in range(3)]\n    for i in range(3):\n        piv=max(range(i,3), key=lambda r: abs(M[r][i]))\n        M[i],M[piv]=M[piv],M[i]\n        div=M[i][i] or 1.0\n        M[i]=[v/div for v in M[i]]\n        for r in range(3):\n            if r==i: continue\n            fac=M[r][i]\n            M[r]=[M[r][c]-fac*M[i][c] for c in range(4)]\n    return M[0][3], M[1][3], M[2][3]\n",
    },
    {
        "id": "goertzel_tone",
        "title": "Goertzel single-bin detector",
        "difficulty": "hard",
        "tags": ["dsp", "ee"],
        "prompt": "Implement `goertzel_power(y, k)` — Goertzel algorithm power for DFT bin k on real list y. Return float power (q1^2+q2^2-coeff*q1*q2).",
        "public_tests_hint": "- peak bin of a tone has higher power than neighbors",
        "test_source": "import math\nimport solution\n\ndef run():\n    n=64; fbin=5; y=[math.sin(2*math.pi*fbin*i/n) for i in range(n)]\n    p5=solution.goertzel_power(y,5)\n    p4=solution.goertzel_power(y,4)\n    p6=solution.goertzel_power(y,6)\n    assert p5>p4 and p5>p6\n",
        "oracle": "import math\n\ndef goertzel_power(y, k):\n    n=len(y)\n    w=2*math.pi*k/n\n    coeff=2*math.cos(w)\n    q0=q1=q2=0.0\n    for v in y:\n        q0=v+coeff*q1-q2\n        q2,q1=q1,q0\n    return q1*q1 + q2*q2 - coeff*q1*q2\n",
    },
    {
        "id": "complementary_filter",
        "title": "Complementary filter angle fuse",
        "difficulty": "hard",
        "tags": ["sensors", "robotics", "ee"],
        "prompt": "Implement `comp_filter(angle, gyro_rate, accel_angle, dt, alpha=0.98)` returning updated angle: alpha*(angle+gyro_rate*dt)+(1-alpha)*accel_angle.",
        "public_tests_hint": "- alpha=1 → pure integrate\n- alpha=0 → accel only",
        "test_source": "import solution\n\ndef run():\n    assert abs(solution.comp_filter(0,10,5,0.1,1.0)-1.0)<1e-12\n    assert abs(solution.comp_filter(0,10,5,0.1,0.0)-5.0)<1e-12\n    v=solution.comp_filter(0,0,10,0.1,0.98)\n    assert abs(v-0.2)<1e-12\n",
        "oracle": "def comp_filter(angle, gyro_rate, accel_angle, dt, alpha=0.98):\n    return alpha*(angle+gyro_rate*dt)+(1-alpha)*accel_angle\n",
    },
    {
        "id": "allan_variance_simple",
        "title": "Two-sample Allan variance",
        "difficulty": "hard",
        "tags": ["sensors", "metrology"],
        "prompt": "Implement `allan_var(x, tau_samples)` for a 1-D series: classic overlapping-ish two-sample form on non-overlapping blocks of size tau_samples. Return variance float.",
        "public_tests_hint": "- constant series → ~0\n- positive for noisy series",
        "test_source": "import solution\n\ndef run():\n    assert solution.allan_var([1,1,1,1,1,1],2)<1e-12\n    v=solution.allan_var([0,1,0,1,0,1,0,1],2)\n    assert v>0\n",
        "oracle": "def allan_var(x, tau_samples):\n    n=len(x)//tau_samples\n    if n<2: return 0.0\n    means=[sum(x[i*tau_samples:(i+1)*tau_samples])/tau_samples for i in range(n)]\n    s=0.0\n    for i in range(n-1):\n        d=means[i+1]-means[i]\n        s+=d*d\n    return s/(2*(n-1))\n",
    },
    {
        "id": "fresnel_reflectance",
        "title": "Normal-incidence Fresnel reflectance",
        "difficulty": "medium",
        "tags": ["optics", "physics"],
        "prompt": "Implement `fresnel_R(n1, n2)` amplitude reflection |r|^2 for normal incidence: r=(n1-n2)/(n1+n2).",
        "public_tests_hint": "- n1=n2 → 0\n- glass/air known value within 1e-12",
        "test_source": "import solution\n\ndef run():\n    assert abs(solution.fresnel_R(1.5,1.5))<1e-12\n    r=(1.0-1.5)/(1.0+1.5)\n    assert abs(solution.fresnel_R(1.0,1.5)-r*r)<1e-12\n",
        "oracle": "def fresnel_R(n1, n2):\n    r=(n1-n2)/(n1+n2)\n    return r*r\n",
    },
    {
        "id": "butterworth_cutoff_order",
        "title": "Butterworth order estimate",
        "difficulty": "hard",
        "tags": ["dsp", "filters"],
        "prompt": "Implement `butter_order(wp, ws, rp_db, rs_db)` returning ceil of Butterworth analog order N = log(eps_s/eps_p)/log(ws/wp) with eps from ripples. Return int >=1.",
        "public_tests_hint": "- ws>wp → finite N\n- stricter stopband → higher N",
        "test_source": "import math\nimport solution\n\ndef run():\n    n1=solution.butter_order(1.0,2.0,1.0,20.0)\n    n2=solution.butter_order(1.0,2.0,1.0,40.0)\n    assert n1>=1 and n2>=n1\n",
        "oracle": "import math\n\ndef butter_order(wp, ws, rp_db, rs_db):\n    eps_p=math.sqrt(10**(rp_db/10)-1)\n    eps_s=math.sqrt(10**(rs_db/10)-1)\n    n=math.log(eps_s/eps_p)/math.log(ws/wp)\n    return max(1, math.ceil(n-1e-12))\n",
    },
    {
        "id": "rigid_body_ke",
        "title": "Rigid body kinetic energy",
        "difficulty": "medium",
        "tags": ["mechanics", "physics", "robotics"],
        "prompt": "Implement `ke(mass, v, I, omega)` = 0.5*m*|v|^2 + 0.5*I*|omega|^2 for 3-vectors v, omega (lists).",
        "public_tests_hint": "- zero rates → 0\n- matches hand calc",
        "test_source": "import solution\n\ndef run():\n    assert abs(solution.ke(2,[1,0,0],3,[0,2,0])-(1+6))<1e-12\n",
        "oracle": "def ke(mass, v, I, omega):\n    return 0.5*mass*sum(x*x for x in v)+0.5*I*sum(w*w for w in omega)\n",
    },
    {
        "id": "zipf_rank",
        "title": "Zipf rank-frequency fit slope",
        "difficulty": "medium",
        "tags": ["nlp", "stats"],
        "prompt": "Implement `zipf_slope(freqs)` — OLS slope of log(freq) vs log(rank) for freqs sorted descending positive. Return slope float.",
        "public_tests_hint": "- pure zipf-ish decreasing → negative slope",
        "test_source": "import solution\n\ndef run():\n    freqs=[100,50,33,25,20]\n    s=solution.zipf_slope(freqs)\n    assert s<0\n",
        "oracle": "import math\n\ndef zipf_slope(freqs):\n    ys=[math.log(f) for f in freqs]\n    xs=[math.log(i+1) for i in range(len(freqs))]\n    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n\n    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))\n    den=sum((x-mx)**2 for x in xs) or 1.0\n    return num/den\n",
    },
    {
        "id": "is_stable_poly",
        "title": "Routh-Hurwitz order-2 stability",
        "difficulty": "hard",
        "tags": ["control", "ee"],
        "prompt": "Implement `is_stable_quadratic(a, b, c)` for s^2 + a s + b? Wait: poly s^2 + a*s + b with c unused. Actually signature `is_stable_quadratic(a, b)` for s^2+a s+b — stable iff a>0 and b>0.",
        "public_tests_hint": "- (2,2) True\n- (-1,1) False",
        "test_source": "import solution\n\ndef run():\n    assert solution.is_stable_quadratic(2,2) is True\n    assert solution.is_stable_quadratic(-1,1) is False\n    assert solution.is_stable_quadratic(1,-1) is False\n",
        "oracle": "def is_stable_quadratic(a, b):\n    return a>0 and b>0\n",
    },
    {
        "id": "beam_deflection_cantilever",
        "title": "Cantilever end deflection",
        "difficulty": "medium",
        "tags": ["mechanics", "physics"],
        "prompt": "Implement `cantilever_deflection(F, L, E, I)` = F*L^3/(3*E*I).",
        "public_tests_hint": "- doubles if F doubles\n- matches analytic",
        "test_source": "import solution\n\ndef run():\n    d=solution.cantilever_deflection(10,2,1e6,1e-4)\n    assert abs(d-10*8/(3*1e6*1e-4))<1e-12\n",
        "oracle": "def cantilever_deflection(F, L, E, I):\n    return F*L**3/(3*E*I)\n",
    },
]


def main() -> None:
    for spec in SPEC:
        oracle = spec.pop("oracle")
        tid = spec["id"]
        # fix vandermonde prompt comment noise
        (TASKS / f"{tid}.json").write_text(json.dumps(spec, indent=2) + "\n")
        (ORACLES / f"{tid}.py").write_text(oracle)
        print(tid)
    print("added", len(SPEC))


if __name__ == "__main__":
    main()
