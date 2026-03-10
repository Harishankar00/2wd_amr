"""
navigation.launch.py
═══════════════════════════════════════════════════════════════════
Launches the full navigation stack for the 2WD AMR.

This file launches Nav2 on top of the simulation (or real robot).
For simulation, start simulation.launch.py first, then this file.

Usage (two terminals):

  Terminal 1 — simulation:
    ros2 launch amr simulation.launch.py

  Terminal 2 — navigation:
    ros2 launch amr navigation.launch.py

  Or combined (simulation + navigation together):
    ros2 launch amr navigation.launch.py launch_sim:=true

Arguments:
  launch_sim (bool, default=false)
      Set true to also start Gazebo via simulation.launch.py
  map (string, default='')
      Full path to a YAML map file. Leave empty to use Nav2 without
      a pre-built map (SLAM mode via slam_toolbox is recommended).
  use_sim_time (bool, default=true)
═══════════════════════════════════════════════════════════════════
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    # ── Package directories ───────────────────────────────────────
    pkg_amr        = get_package_share_directory('amr')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    # ── File paths ────────────────────────────────────────────────
    nav2_params   = os.path.join(pkg_amr, 'config', 'nav2_params.yaml')
    sim_launch    = os.path.join(pkg_amr, 'launch', 'simulation.launch.py')

    # ── Launch arguments ─────────────────────────────────────────
    declare_launch_sim = DeclareLaunchArgument(
        name='launch_sim',
        default_value='false',
        description='Also launch Gazebo simulation alongside Nav2',
    )

    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation clock',
    )

    declare_map = DeclareLaunchArgument(
        name='map',
        default_value='',
        description='Full path to map YAML file (leave empty for no map)',
    )

    declare_autostart = DeclareLaunchArgument(
        name='autostart',
        default_value='true',
        description='Automatically start Nav2 lifecycle nodes',
    )

    launch_sim    = LaunchConfiguration('launch_sim')
    use_sim_time  = LaunchConfiguration('use_sim_time')
    map_yaml      = LaunchConfiguration('map')
    autostart     = LaunchConfiguration('autostart')

    # ── Optional: launch simulation first ────────────────────────
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(sim_launch),
        condition=IfCondition(launch_sim),
    )

    # ── Nav2 bringup ─────────────────────────────────────────────
    #    Uses the official nav2_bringup launch which accepts params_file.
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time':  use_sim_time,
            'params_file':   nav2_params,
            'map':           map_yaml,
            'autostart':     autostart,
        }.items(),
    )

    return LaunchDescription([
        declare_launch_sim,
        declare_use_sim_time,
        declare_map,
        declare_autostart,
        simulation,
        nav2_bringup,
    ])
