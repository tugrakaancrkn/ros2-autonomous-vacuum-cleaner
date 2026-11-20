import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from vacuum_cleaner_interfaces.msg import TelemetryStream
from vacuum_cleaner_interfaces.action import OperationalExecution


class TaskManager(Node):

    def __init__(self):
        super().__init__('task_manager')

        self.callback_group_ = ReentrantCallbackGroup()

        self.battery_level_ = 100
        self.dustbin_full_ = False
        self.hazard_sensor_ = 0

        self.status_subscriber_ = self.create_subscription(
            TelemetryStream, '/vacuum/status', self.telemetry_callback, 10, callback_group=self.callback_group_)

        self.action_server_ = ActionServer(
            self,
            OperationalExecution,
            '/vacuum/execute_cleaning',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group_
        )

        self.get_logger().info('Task Manager ready and waiting for cleaning goals...')

    def telemetry_callback(self, msg):
        self.battery_level_ = msg.battery_level
        self.dustbin_full_ = msg.dustbin_fullness_status
        self.hazard_sensor_ = msg.hazard_sensor

    def goal_callback(self, goal_request):
        self.get_logger().info(
            f'Goal received -> mode: {goal_request.mode}, power_mode: {goal_request.power_mode}'
        )

        if self.battery_level_ < 15:
            self.get_logger().warn(
                f'Goal REJECTED: Battery too low ({self.battery_level_}%).'
            )
            return GoalResponse.REJECT

        if self.dustbin_full_:
            self.get_logger().warn('Goal REJECTED: Dustbin is full.')
            return GoalResponse.REJECT

        self.get_logger().info('Goal ACCEPTED.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received. Stopping task...')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        mode = goal_handle.request.mode
        power_mode = goal_handle.request.power_mode
        self.get_logger().info(
            f'Executing cleaning -> mode: {mode}, power_mode: {power_mode}'
        )

        feedback_msg = OperationalExecution.Feedback()
        result = OperationalExecution.Result()

        rooms = ['Living Room', 'Kitchen', 'Hallway', 'Bedroom', 'Bathroom']
        total_steps = 10
        area_per_step = 5
        total_area = 0
        start_time = time.time()

        for step in range(1, total_steps + 1):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.total_area_cleaned = int(total_area)
                result.total_elapsed_time = int(time.time() - start_time)
                result.completion_info = f'Canceled during {mode} ({power_mode}).'
                self.get_logger().info(result.completion_info)
                return result

            if self.battery_level_ <= 10:
                goal_handle.abort()
                result.total_area_cleaned = int(total_area)
                result.total_elapsed_time = int(time.time() - start_time)
                result.completion_info = 'Aborted: Critical battery level.'
                self.get_logger().error(result.completion_info)
                return result

            if self.dustbin_full_:
                goal_handle.abort()
                result.total_area_cleaned = int(total_area)
                result.total_elapsed_time = int(time.time() - start_time)
                result.completion_info = 'Aborted: Dustbin became full.'
                self.get_logger().warn(result.completion_info)
                return result

            if self.hazard_sensor_ != 0:
                self.get_logger().warn(
                    f'Hazard detected (code: {self.hazard_sensor_}). Avoiding obstacle...'
                )

            total_area += area_per_step
            room_index = min((step - 1) * len(rooms) // total_steps, len(rooms) - 1)

            feedback_msg.current_active_room = rooms[room_index]
            feedback_msg.battery_state = f'{self.battery_level_}%'
            feedback_msg.completion_percentage = int(step * 10)
            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(
                f'Room: {feedback_msg.current_active_room} | '
                f'Progress: {feedback_msg.completion_percentage}% | '
                f'Battery: {feedback_msg.battery_state}'
            )
            time.sleep(1.0)

        goal_handle.succeed()
        result.total_area_cleaned = int(total_area)
        result.total_elapsed_time = int(time.time() - start_time)
        result.completion_info = f'Completed successfully (mode={mode}, power_mode={power_mode}).'
        self.get_logger().info(result.completion_info)
        return result


def main(args=None):
    rclpy.init(args=args)
    task_manager = TaskManager()

    executor = MultiThreadedExecutor()
    executor.add_node(task_manager)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        task_manager.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()