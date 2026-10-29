import math

def butter_order(wp, ws, rp_db, rs_db):
    eps_p=math.sqrt(10**(rp_db/10)-1)
    eps_s=math.sqrt(10**(rs_db/10)-1)
    n=math.log(eps_s/eps_p)/math.log(ws/wp)
    return max(1, math.ceil(n-1e-12))
