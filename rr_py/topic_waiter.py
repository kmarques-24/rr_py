# Triggers an exit when both /scan and /points start receiving data

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy 

class TopicWaiter(Node):
    def __init__(self):
        super().__init__('topic_waiter')
        self.scan_received   = False
        self.points_received = False

        # ToF publishes reliable to /points for packet breakup, so need to match
        points_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        scan_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self.sub_scan   = self.create_subscription(
            LaserScan,    '/scan',   self.scan_cb,   scan_qos)
        self.sub_points = self.create_subscription(
            PointCloud2,  '/points', self.points_cb, points_qos)

        self.get_logger().info('Waiting for /scan and /points...')

    def scan_cb(self, msg):
        if not self.scan_received:
            self.get_logger().info('/scan received')
        self.scan_received = True
        self.check_done()

    def points_cb(self, msg):
        if not self.points_received:
            self.get_logger().info('/points received')
        self.points_received = True
        self.check_done()

    def check_done(self):
        if self.scan_received and self.points_received:
            self.get_logger().info('Both topics live — triggering SLAM and bag')
            raise SystemExit(0) # better alternative to rclpy.shutdown()

def main():
    rclpy.init()
    rclpy.spin(TopicWaiter())

if __name__ == '__main__':
    main()