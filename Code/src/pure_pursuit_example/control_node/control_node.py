#!/usr/bin/env python3
import math
import numpy as np

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive


from .control_logic import compute_command


def quaternion_to_yaw(x, y, z, w):
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

def load_trajectory(path):
    data = np.genfromtxt(path, delimiter=',', skip_header=1)
    waypoints = data[:, 0:2]   # pose.x, pose.y
    speeds = data[:, 3]        # linear.x
    return waypoints, speeds


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # Load the trajectory to follow
        self.declare_parameter('trajectory_file', 'map/opt.trj')
        path = self.get_parameter('trajectory_file').value
        self.waypoints, self.speeds = load_trajectory(path)

        # ROS subscriber and publisher
        self.sub = self.create_subscription(
            Odometry, '/ego_racecar/odom', self.pose_callback, 10)
        self.pub = self.create_publisher(AckermannDriveStamped, '/drive', 10)
        self.trj_pub = self.create_publisher(Path, '/trajectory', 10)
        self.trj_timer = self.create_timer(1.0, self.publish_trajectory)
        self.goal_pub = self.create_publisher(PoseStamped, '/goal', 10)
    
    def publish_trajectory(self):
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        for (x, y) in self.waypoints:
            pose = PoseStamped()
            pose.pose.position.x = x
            pose.pose.position.y = y
    
            path_msg.poses.append(pose)
        self.trj_pub.publish(path_msg)

    def pose_callback(self, pose_msg):
        # Current pose
        p = pose_msg.pose.pose.position
        q = pose_msg.pose.pose.orientation
        current_speed = pose_msg.twist.twist.linear.x
        yaw = quaternion_to_yaw(q.x, q.y, q.z, q.w)

        # Pure pursuit -> steering + speed
        steer, speed, gx, gy = compute_command(
            self.waypoints, self.speeds, p.x, p.y, yaw, current_speed)
        
        # Pub goal
        goal_msg = PoseStamped()
        goal_msg.header.frame_id = 'map'
        goal_msg.pose.position.x = gx
        goal_msg.pose.position.y = gy
        self.goal_pub.publish(goal_msg)
        # Publish drive message
        msg = AckermannDriveStamped()
        msg.drive.steering_angle = float(steer)
        msg.drive.speed = float(speed)
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    print("ControlNode Initialized")
    pure_pursuit_node = ControlNode()
    rclpy.spin(pure_pursuit_node)

    pure_pursuit_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()