import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32 # Match the type used in micro-ROS

class MicroRosSubscriber(Node):

    def __init__(self):
        super().__init__('microros_subscriber')
        
        # Ensure the topic name and message type match the micro-ROS node
        self.subscription = self.create_subscription(
            Float32,
            'float32publisher',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Received: "%d"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    subscriber = MicroRosSubscriber()
    rclpy.spin(subscriber)
    subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
