import rclpy
from rclpy.node import Node
from vacuum_cleaner_interfaces.msg import TelemetryStream
from random import randint

class VacuumHardwareDriver(Node):

    def __init__(self):
        super().__init__('vacuum_hardware_driver')
        self.status_publisher_ = self.create_publisher(TelemetryStream, "/vacuum/status", 10)
        self.streaming_timer_ = self.create_timer(1.0, self.status_callback)
        self.dustbin_fullness_status_ = False
        self.dustbin_fullness_ = 0
        self.battery_level_ = 100
        self.hazard_state_ = 0

    def status_callback(self):
        msg = TelemetryStream()
        if self.battery_level_ != 0:
            msg.battery_level = self.battery_level_ - 1
            self.battery_level_ = msg.battery_level
        else:
            self.get_logger().info("Battery percentage 0% , please charge.")

        if self.dustbin_fullness_ > 49:
            self.dustbin_fullness_status_ = True
        msg.dustbin_fullness_status = self.dustbin_fullness_status_
        self.dustbin_fullness_ += randint(0,7)

        random_event = randint(0, 100)
        if random_event < 80:
            self.hazard_state_ = 0
        else:
            self.hazard_state_ = randint(1,3)
        msg.hazard_sensor = self.hazard_state_

        self.status_publisher_.publish(msg)
        

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = VacuumHardwareDriver()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()