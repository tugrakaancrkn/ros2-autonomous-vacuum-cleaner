import rclpy
from rclpy.node import Node
from vacuum_cleaner_interfaces.srv import FloorLevelConfiguration

class MapLoader(Node):

    def __init__(self):
        super().__init__('map_loader')
        self.map_loader_service_ = self.create_service(
            FloorLevelConfiguration, "/vacuum/set_floor_level", self.floor_level_callback)
        self.floors_ = {0 : "Floor_0", 1 : "Floor_1", 2 : " Floor_2"}
        self.current_floor_ = 0
        self.get_logger().info(f"Map Loader ready. Current Map: {self.floors_.get(self.current_floor_)}")


    def floor_level_callback(self, request, response):
        requested_floor = request.floor_id

        if requested_floor in self.floors_:
            self.current_floor_ = requested_floor
            loaded_map = self.floors_[self.current_floor_]
            response.success = True
            response.info = f"Loaded map: {loaded_map}"
            self.get_logger().info(f"Floor updated -> {loaded_map}")

        else:
            valid_floors = list(self.floors_.keys())
            response.success = False
            response.info = (
                f'Invalid floor level ({requested_floor}). '
                f'Available floors: {valid_floors}'
            )
            self.get_logger().warn(response.info)

        return response


def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MapLoader()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()