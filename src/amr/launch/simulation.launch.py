"""
simulation.launch.py
═══════════════════════════════════════════════════════════════════
Full simulation bringup for the 2WD AMR in Gazebo Harmonic.

Launch sequence:
  1. Gazebo Harmonic (gz sim -r <world>)
  2. robot_state_publisher   (publishes /robot_description + static TF)
  3. ros_gz_sim create       (spawns URDF into Gazebo)
  4. ros_gz_bridge           (bridges Gz ↔ ROS2 topics)

NOTE: joint_state_publisher is NOT launched here. The Gazebo
JointStatePublisher plugin + ros_gz_bridge provides /joint_states.
═══════════════════════════════════════════════════════════════════
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    LaunchConfiguration,
)
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue


def generate_launch_description():

    pkg_amr        = get_package_share_directory('amr')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_file  = os.path.join(pkg_amr, 'world', 'warehouse.world')
    bridge_yaml = os.path.join(pkg_amr, 'config', 'ros_gz_bridge.yaml')
    urdf_model  = os.path.join(pkg_amr, 'description', 'amr.urdf.xacro')

    # ── Launch arguments ─────────────────────────────────────────
    declare_spawn_x = DeclareLaunchArgument(
        'spawn_x', default_value='0.0', description='Robot spawn X')
    declare_spawn_y = DeclareLaunchArgument(
        'spawn_y', default_value='0.0', description='Robot spawn Y')
    declare_spawn_yaw = DeclareLaunchArgument(
        'spawn_yaw', default_value='0.0', description='Robot spawn yaw (rad)')

    spawn_x   = LaunchConfiguration('spawn_x')
    spawn_y   = LaunchConfiguration('spawn_y')
    spawn_yaw = LaunchConfiguration('spawn_yaw')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_model]),
        value_type=str,
    )

    # ── 1. Gazebo Harmonic ────────────────────────────────────────
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r ', world_file],
            'on_exit_shutdown': 'true',
        }.items(),
    )

    # ── 2. Robot State Publisher (NO joint_state_publisher in sim) ─
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    # ── 3. Spawn robot ────────────────────────────────────────────
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                name='spawn_amr',
                arguments=[
                    '-name',  'amr',
                    '-topic', '/robot_description',
                    '-x',     spawn_x,
                    '-y',     spawn_y,
                    '-z',     '0.06',
                    '-Y',     spawn_yaw,
                ],
                output='screen',
            ),
        ],
    )

    # ── 4. ros_gz_bridge ─────────────────────────────────────────
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            '--ros-args',
            '-p', ['config_file:=', bridge_yaml],
        ],
        output='screen',
    )

    return LaunchDescription([
        declare_spawn_x,
        declare_spawn_y,
        declare_spawn_yaw,
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge,
    ])
