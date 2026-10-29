def rotate_vector(q, v):
    w, x, y, z = q
    vx, vy, vz = v
    # t = 2 * cross(q_vec, v)
    tx = 2 * (y * vz - z * vy)
    ty = 2 * (z * vx - x * vz)
    tz = 2 * (x * vy - y * vx)
    # v' = v + w*t + cross(q_vec, t)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )
