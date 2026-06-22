#!/usr/bin/env python3
import math
import numpy as np
# Control logic for pure pursuit controller
# Tunables
MIN_LOOKAHEAD = 0.3    # [m] minimun lookahead distance
LOOKAHEAD_GAIN = 0.3   # [s] lookahead distance gain
WHEELBASE = 0.33       # [m] F1TENTH wheelbase
MAX_STEER = 0.36       # [rad] steering limit


def find_target(waypoints, x, y, lookahead):
    #find the target the will be used for the pure pursuit controller
    dists = np.linalg.norm(waypoints - [x, y], axis=1)
    nearest = int(np.argmin(dists))
    n = len(waypoints)
    for k in range(n):
        i = (nearest + k) % n
        if np.linalg.norm(waypoints[i] - [x, y]) >= lookahead:
            return i
    return nearest


def compute_command(waypoints, speeds, x, y, yaw, current_speed):
    # compute actual command for the vehicle
    lookahead = MIN_LOOKAHEAD + current_speed * LOOKAHEAD_GAIN  # [m] lookahead distance
    i = find_target(waypoints, x, y, lookahead)
    gx, gy = waypoints[i]

    # Goal in the car's frame (+x forward, +y left)
    dx, dy = gx - x, gy - y
    y_car = -math.sin(yaw) * dx + math.cos(yaw) * dy

    # Pure pursuit steering, then clamp
    steer = math.atan(2.0 * WHEELBASE * y_car / lookahead**2)
    steer = max(-MAX_STEER, min(MAX_STEER, steer))

    return steer, speeds[i], gx, gy

