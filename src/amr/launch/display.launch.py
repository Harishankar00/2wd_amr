"""
display.launch.py
═══════════════════════════════════════════════════════════════════
Launches robot_state_publisher + RViz2 for offline robot inspection
(no simulation required). Useful for checking the URDF model.

Usage:
  ros2 launch amr display.launch.py
  ros2 launch amr display.launch.py use_gui:=true   # with joint sliders
═══════════════════════════════════════════════════════════════════
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_amr = get_package_share_directory('amr')

    rviz_config = os.path.join(pkg_amr, 'config', 'amr_rviz.rviz')

    declare_use_gui = DeclareLaunchArgument(
        name='use_gui',
        default_value='true',
        description='Launch joint_state_publisher_gui for interactive joint control',
    )

    # Include robot_state.launch.py with GUI enabled
    robot_state = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_amr, 'launch', 'robot_state.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'false',
            'use_gui': LaunchConfiguration('use_gui'),
        }.items(),
    )

    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': False}],
        output='screen',
    )

    return LaunchDescription([
        declare_use_gui,
        robot_state,
        rviz2,
    ])
