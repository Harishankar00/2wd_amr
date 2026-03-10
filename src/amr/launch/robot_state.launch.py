"""
robot_state.launch.py
═══════════════════════════════════════════════════════════════════
Launches:
  • robot_state_publisher  — publishes /robot_description + static TF
  • joint_state_publisher  — provides zero joint states for non-driven joints
                             (in sim, wheel states come from ros_gz_bridge)

Arguments:
  use_sim_time (bool, default=false) — pass true when running with Gazebo
═══════════════════════════════════════════════════════════════════
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_amr = get_package_share_directory('amr')
    urdf_model = os.path.join(pkg_amr, 'description', 'amr.urdf.xacro')

    # ── Launch arguments ──────────────────────────────────────────
    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true',
    )

    declare_use_gui = DeclareLaunchArgument(
        name='use_gui',
        default_value='false',
        description='Start joint_state_publisher_gui if true (RViz tuning)',
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_gui = LaunchConfiguration('use_gui')

    # ── Expand xacro → URDF string at launch time ─────────────────
    # Wrapped in ParameterValue(value_type=str) so ROS2 Jazzy doesn't
    # try to auto-parse the raw XML as YAML.
    robot_description = ParameterValue(
        Command(['xacro ', urdf_model]),
        value_type=str,
    )

    # ── robot_state_publisher ─────────────────────────────────────
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
    )

    # ── joint_state_publisher (headless — used in sim / real robot)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=UnlessCondition(use_gui),
    )

    # ── joint_state_publisher_gui (interactive sliders — for RViz)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_gui),
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_use_gui,
        robot_state_publisher,
        joint_state_publisher,
        joint_state_publisher_gui,
    ])
