#!/usr/bin/env python3
import sys
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDrive, AckermannDriveStamped
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

from .preprocessing import mean_filter, restrict_fov, propagate_corners, add_margin


class ReactiveFollowGap(Node):

    def __init__(self):
        super().__init__('FollowGap_node')

        self.past_angle = 0.0
        
        # Declare ROS parameters
        self.declare_parameter('mean_filter_window', 10)
        self.declare_parameter('fov_degree', 120.0)
        self.declare_parameter('car_half_width', 0.15)
        self.declare_parameter('margin', 0.10)
        self.declare_parameter('disp_threshold', 0.3)
        self.declare_parameter('gap_threshold', 1.5)
        self.declare_parameter('velocity_gain', 0.5)
        self.declare_parameter('max_velocity', 2.0)
        self.declare_parameter('min_velocity', 0.5)
        
        # Get parameters from ROS parameter server
        self.mean_filter_window = self.get_parameter('mean_filter_window').value
        self.fov_degree = self.get_parameter('fov_degree').value
        self.car_half_width = self.get_parameter('car_half_width').value
        self.margin = self.get_parameter('margin').value
        self.disp_threshold = self.get_parameter('disp_threshold').value
        self.gap_threshold = self.get_parameter('gap_threshold').value
        self.velocity_gain = self.get_parameter('velocity_gain').value
        self.max_velocity = self.get_parameter('max_velocity').value
        self.min_velocity = self.get_parameter('min_velocity').value

        # QoS profile compatible with typical LIDAR publishers (sensor data QoS)
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscriptions, Publishers
        self.lidar_sub = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, qos)
        self.drive_pub = self.create_publisher(AckermannDriveStamped, 'drive', 1)
        self.gap_marker_pub = self.create_publisher(Marker, 'gap_marker', 1)
        self.processed_scan_pub = self.create_publisher(LaserScan, 'processed_scan', 1)

    
    def preprocess_lidar(self, ranges, data):
        ranges, self.fov_start, self.fov_end = restrict_fov(ranges, data, self.fov_degree)
        ranges = propagate_corners(ranges, data.angle_increment, self.car_half_width, self.margin, self.disp_threshold)

        return ranges

    def find_max_gap(self, ranges, threshold=1.5):
        best_start, best_end = 0, 0
        best_len = 0

        cur_start = None
        for i, r in enumerate(ranges):
            if r > threshold:
                if cur_start is None:
                    cur_start = i
            else:
                if cur_start is not None:
                    length = i - cur_start
                    if length > best_len:
                        best_len = length
                        best_start, best_end = cur_start, i
                    cur_start = None

        # handle case where the free run goes to the end of the array
        if cur_start is not None:
            length = len(ranges) - cur_start
            if length > best_len:
                best_start, best_end = cur_start, len(ranges)

        return best_start, best_end

    def find_farthest_point(self, start_i, end_i, ranges):
        max_value = 0
        max_ind = 0

        for i in range(start_i, end_i):
            if ranges[i] > max_value:
                max_value = ranges[i]
                max_ind = i
        return max_ind

    def publish_target_marker(self, direction, angle, ranges, frame_id, stamp):
        m = Marker()
        m.header.frame_id = frame_id
        m.header.stamp = stamp
        m.id = 0
        m.type = Marker.LINE_STRIP
        m.action = Marker.ADD
        m.scale.x = 0.1
        m.color.g = 1.0
        m.color.a = 1.0

        p0 = Point()  # car origin
        m.points.append(p0)

        ang = math.radians(angle)
        r = ranges[direction] if ranges[direction] > 0 else 1.0
        p1 = Point()
        p1.x = r * math.cos(ang)
        p1.y = r * math.sin(ang)
        m.points.append(p1)

        self.gap_marker_pub.publish(m)

    def lidar_callback(self, data):
        ranges = self.preprocess_lidar(list(data.ranges), data)
        # Publish processed scan for visualization/debugging
        processed_scan = LaserScan()
        processed_scan = data
        processed_scan.ranges = ranges
        self.processed_scan_pub.publish(processed_scan) 

        # Find max length gap
        s, e = self.find_max_gap(ranges, threshold=self.gap_threshold)

        # Find the best point in the gap
        direction = self.find_farthest_point(s, e, ranges)
        angle = math.degrees(data.angle_min + (float(direction) * data.angle_increment))
        self.publish_target_marker(direction, angle, ranges, data.header.frame_id, self.get_clock().now().to_msg())

        # pid angle
        steer = angle * 0.0075

        # clamp for the steer
        if steer > 0.5:
            steer = 0.5
        elif steer < -0.5:
            steer = -0.5

        # velocity
        vel = self.velocity_gain * data.ranges[direction]
        if vel > self.max_velocity:
                vel = self.max_velocity
        if vel < self.min_velocity:
            vel = self.min_velocity

        # Publish Drive message
        msg = AckermannDriveStamped()
        msg.drive.speed = vel
        msg.drive.steering_angle = steer
        self.drive_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    rfgs = ReactiveFollowGap()
    rclpy.spin(rfgs)
    rfgs.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main(sys.argv)