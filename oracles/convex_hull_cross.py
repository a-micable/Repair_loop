def orient(ax,ay,bx,by,cx,cy):
    val=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
    if abs(val)<1e-12:
        return 0
    return 1 if val>0 else -1
