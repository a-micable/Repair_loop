def ke(mass, v, I, omega):
    return 0.5*mass*sum(x*x for x in v)+0.5*I*sum(w*w for w in omega)
