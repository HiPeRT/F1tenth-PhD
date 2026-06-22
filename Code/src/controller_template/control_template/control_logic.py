#!/usr/bin/env python3
import math
import numpy as np

# you can put global variable you need here, like vehicle parameters, tunable parameters, etc.
# For example:
# L = 0.33  # wheelbase



def compute_command(waypoints, speeds, x, y, yaw, current_speed):
    # waypoints: list of (x, y) coordinates of the trajectory
    # speeds: list of desired speeds at each waypoint
    # x, y, yaw: current pose of the vehicle
    # current_speed: current speed of the vehicle
    
    # add your control algorithm here
    # typically you will find the nearest waypoint, compute the desired steering angle and speed, and return them as a command
    return 0, 0, 0, 0
