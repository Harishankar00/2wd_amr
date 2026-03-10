# 2WD Autonomous Mobile Robot (AMR)

**ROS2 Jazzy + Gazebo Harmonic + Ubuntu 24.04**

A minimal, stable codebase for a 2-wheel differential drive AMR with 2D LiDAR — designed for both Gazebo simulation and real-robot deployment.

---

## Robot Specifications

| Property | Value |
|---|---|
| Type | 2WD Differential Drive |
| Total Mass | 16 kg |
| Base (L × W × H) | 0.52 × 0.42 × 0.11 m |
| Wheel Radius | 0.06 m |
| Wheel Separation | 0.32 m |
| Max Speed | 1.0 m/s |
| LiDAR Range | 12 m / 360° / 720 samples |

---

## Package Structure

```
2wd_amr/
└── src/
    └── amr/
        ├── description/
        │   ├── amr.urdf.xacro     # Full robot model
        │   ├── materials.xacro    # Visual materials
        │   └── sensors.xacro     # 2D LiDAR (Gazebo Harmonic gpu_lidar)
        ├── world/
        │   └── warehouse.world   # SDF world (Gazebo Harmonic)
        ├── config/
        │   ├── diff_drive.yaml      # Drive parameters (reference)
        │   ├── lidar.yaml           # LiDAR parameters (reference)
        │   ├── ros_gz_bridge.yaml   # Topic bridge config (Gz ↔ ROS2)
        │   ├── nav2_params.yaml     # Full Nav2 parameter set
        │   └── amr_rviz.rviz        # RViz2 display config
        └── launch/
            ├── display.launch.py      # URDF view in RViz (no Gazebo)
            ├── robot_state.launch.py  # robot_state_publisher + jsp
            ├── simulation.launch.py   # Full Gazebo simulation
            └── navigation.launch.py  # Simulation + Nav2
```

---

## TF Tree

```
map
└── odom
    └── base_link
        ├── left_wheel_link
        ├── right_wheel_link
        ├── caster_front_link
        ├── caster_rear_link
        └── lidar_link   ← always child of base_link (scan stays stable)
```

---

## Prerequisites

```bash
sudo apt install ros-jazzy-ros-gz \
                 ros-jazzy-ros-gz-bridge \
                 ros-jazzy-ros-gz-sim \
                 ros-jazzy-nav2-bringup \
                 ros-jazzy-robot-state-publisher \
                 ros-jazzy-joint-state-publisher \
                 ros-jazzy-joint-state-publisher-gui \
                 ros-jazzy-xacro \
                 ros-jazzy-rviz2
```

---

## Build

```bash
cd ~/2wd_amr
source /opt/ros/jazzy/setup.bash
colcon build --packages-select amr
source install/setup.bash
```

---

## Usage

### 1. Inspect URDF in RViz (no Gazebo)
```bash
ros2 launch amr display.launch.py
```

### 2. Launch Simulation
```bash
ros2 launch amr simulation.launch.py
```

### 3. Drive the robot
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}"
```

### 4. Launch Navigation (Nav2 + Gazebo)
```bash
ros2 launch amr navigation.launch.py launch_sim:=true
```

### 5. Navigation with a pre-built map
```bash
ros2 launch amr navigation.launch.py \
  launch_sim:=true \
  map:=/path/to/your/map.yaml
```

---

## Key Topics

| Topic | Type | Direction |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | → Robot |
| `/odom` | `nav_msgs/msg/Odometry` | ← Robot |
| `/scan` | `sensor_msgs/msg/LaserScan` | ← LiDAR |
| `/tf` | `tf2_msgs/msg/TFMessage` | ← Plugin |
| `/clock` | `rosgraph_msgs/msg/Clock` | ← Gazebo |
| `/joint_states` | `sensor_msgs/msg/JointState` | ← Gazebo |

---

## Design Notes

- **LiDAR frame stability**: `lidar_link` is a direct child of `base_link` (not the world), ensuring scan data rotates correctly with the robot.
- **Bridge architecture**: `ros_gz_bridge` handles all Gazebo ↔ ROS2 topic translation; no manual republisher nodes needed.
- **Caster wheels**: Friction `μ = 0.0` — free rolling to avoid steering interference.
- **Sim time**: All nodes launched with `use_sim_time:=true` in simulation mode.
