def comp_filter(angle, gyro_rate, accel_angle, dt, alpha=0.98):
    return alpha*(angle+gyro_rate*dt)+(1-alpha)*accel_angle
