def kalman_update(x, P, z, R):
    K=P/(P+R)
    x_new=x+K*(z-x)
    P_new=(1-K)*P
    return x_new, P_new
