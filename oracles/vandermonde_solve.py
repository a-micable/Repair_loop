def fit_quadratic(xs, ys):
    # solve Vandermonde for 3 pts via Cramer's / elimination
    x0,x1,x2=xs; y0,y1,y2=ys
    # use Lagrange then expand — stable enough for public pts
    def lag(x):
        return (
            y0*(x-x1)*(x-x2)/((x0-x1)*(x0-x2))
            + y1*(x-x0)*(x-x2)/((x1-x0)*(x1-x2))
            + y2*(x-x0)*(x-x1)/((x2-x0)*(x2-x1))
        )
    # sample three equations by expanding via finite points already known; fit with np-free LS on powers
    A=[[x*x, x, 1.0] for x in xs]
    # Gaussian elimination
    M=[A[i]+[ys[i]] for i in range(3)]
    for i in range(3):
        piv=max(range(i,3), key=lambda r: abs(M[r][i]))
        M[i],M[piv]=M[piv],M[i]
        div=M[i][i] or 1.0
        M[i]=[v/div for v in M[i]]
        for r in range(3):
            if r==i: continue
            fac=M[r][i]
            M[r]=[M[r][c]-fac*M[i][c] for c in range(4)]
    return M[0][3], M[1][3], M[2][3]
