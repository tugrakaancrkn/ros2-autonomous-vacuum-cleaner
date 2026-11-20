# ROS 2 Autonomous Home Vacuum Cleaner

A modular ROS 2 workspace implementing a simulated autonomous home vacuum cleaner system. The architecture separates custom communication interfaces, core runtime nodes, and XML-based bringup orchestration across three dedicated packages.

## Workspace Architecture

```text
src/
├── vacuum_cleaner_interfaces/         # Custom .msg, .srv, and .action definitions (CMake)
├── autonomous_home_vacuum_cleaner/    # Core Python nodes (hardware driver, map loader, task manager)
└── vacuum_cleaner_bringup/            # Unified XML launch files (CMake)
```

### Core Nodes
* **`vacuum_hardware_driver`**: Simulates low-level hardware telemetry (battery percentage, dust bin status, and obstacle/hazard sensor codes) and publishes updates at 1 Hz.
* **`map_loader`**: Manages multi-floor map state (default: `Floor_0`) and exposes a synchronous configuration service.
* **`task_manager`**: Subscribes to hardware telemetry and acts as an asynchronous Action Server to coordinate room-by-room cleaning routines, obstacle hazard avoidance, live progress feedback, and safe task cancellation.

## Communication Interfaces

| Mechanism | Name | Interface Type | Description |
| :--- | :--- | :--- | :--- |
| **Topic** | `/vacuum/status` | `vacuum_cleaner_interfaces/msg/TelemetryStream` | 1 Hz live hardware telemetry stream |
| **Service** | `/vacuum/set_floor_level` | `vacuum_cleaner_interfaces/srv/FloorLevelConfiguration` | Synchronous floor/map switching |
| **Action** | `/vacuum/execute_cleaning` | `vacuum_cleaner_interfaces/action/OperationalExecution` | Goal-based cleaning execution, feedback, and cancellation |

## Prerequisites

* Ubuntu Linux with ROS 2 installed (e.g., ROS 2 Jazzy / Humble)
* `colcon` build tools (`python3-colcon-common-extensions`)
* `rqt`, `rqt_graph`, and `rqt_topic` (for runtime inspection)

## Installation and Build

1. Clone this repository into your workspace:
   ```bash
   git clone [https://github.com/tugrakaancrkn/ros2-autonomous-vacuum-cleaner.git](https://github.com/tugrakaancrkn/ros2-autonomous-vacuum-cleaner.git)
   cd ros2-autonomous-vacuum-cleaner
   ```
2. Source your ROS 2 installation and compile the workspace:
   ```bash
   source /opt/ros/jazzy/setup.bash
   colcon build
   source install/setup.bash
   ```

## Usage (System Bringup)

Launch all three core nodes simultaneously using the bringup package:

```bash
ros2 launch vacuum_cleaner_bringup vacuum_cleaner.launch.xml
```

Expected startup logs confirm that `vacuum_hardware_driver`, `map_loader` (`Current Map: Floor_0`), and `task_manager` are active.

## Verification & Testing

With the launch file running, open a new terminal (and run `source install/setup.bash`) to test each communication layer:

### 1. Computation Graph (V1)
```bash
rqt_graph
```
Displays `/vacuum_hardware_driver` -> `/vacuum/status` -> `/task_manager`, alongside the standalone `/map_loader` service node.

### 2. Live Telemetry Monitoring (V2)
```bash
rqt
```
Open **Plugins -> Topics -> Topic Monitor** and enable `/vacuum/status` to observe live 1 Hz telemetry updates.

### 3. Floor Level Service Call (V3)
Inspect the service interface and invoke a floor change:
```bash
ros2 service list -t
ros2 interface show vacuum_cleaner_interfaces/srv/FloorLevelConfiguration
ros2 service call /vacuum/set_floor_level vacuum_cleaner_interfaces/srv/FloorLevelConfiguration "{floor_id: 'Floor_1'}"
```

### 4. Cleaning Action Execution & Cancellation (V4)
Send a cleaning goal with live feedback:
```bash
ros2 action send_goal --feedback /vacuum/execute_cleaning vacuum_cleaner_interfaces/action/OperationalExecution "{mode: 'auto', power_mode: 'turbo'}"
```
* Let the 10-step routine complete to verify room-by-room feedback (`Living Room`, `Kitchen`, `Hallway`, `Bedroom`, `Bathroom`), hazard warnings, and the final `SUCCEEDED` result.
* Press **`Ctrl+C`** mid-execution to verify safe goal preemption and `CANCELED` termination.

## Author

* **Tuğra Kaan Çirkin** — Department of Control and Automation Engineering, Istanbul Technical University
