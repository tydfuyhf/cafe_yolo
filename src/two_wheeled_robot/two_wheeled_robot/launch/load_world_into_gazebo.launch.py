# Author: Addison Sears-Collins
# Date: September 19, 2021 (Modified: September 30, 2025)
# Description: Load a world file into Gazebo and spawn a TurtleBot3 Waffle Pi.
# https://automaticaddison.com

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

  # Set the path to the Gazebo ROS package
  pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')   
  
  # Set the path to this package.
  pkg_share = FindPackageShare(package='two_wheeled_robot').find('two_wheeled_robot')

  # Set the path to the world file
  world_file_name = 'cafe.world'
  world_path = os.path.join(pkg_share, 'worlds', world_file_name)
  
  # Set the path to the SDF model files.
  gazebo_models_path = os.path.join(pkg_share, 'models')
  os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

  # -------------------- TURTLEBOT3 PATHS & CONFIGURATION --------------------

  # 1. Set the path to the TurtleBot3 gazebo package for the spawn launch file
  pkg_turtlebot_gazebo = FindPackageShare(package='turtlebot3_gazebo').find('turtlebot3_gazebo')
  spawn_launch_file = os.path.join(pkg_turtlebot_gazebo, 'launch', 'spawn_entity.launch.py')

  # 2. Set the path to the TurtleBot3 XACRO file for Robot State Publisher (RSP)
  # ROS 시스템 경로('/opt/ros/humble/share/...')를 FindPackageShare가 자동으로 찾아줍니다.
  pkg_turtlebot_description = FindPackageShare(package='turtlebot3_description').find('turtlebot3_description')
  xacro_file_path = os.path.join(pkg_turtlebot_description, 'urdf', 'turtlebot3_waffle.urdf.xacro')

  ########### YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE ##############  
  # Launch configuration variables specific to simulation
  headless = LaunchConfiguration('headless')
  use_sim_time = LaunchConfiguration('use_sim_time')
  use_simulator = LaunchConfiguration('use_simulator')
  world = LaunchConfiguration('world')
  
  # ----------------------- NEW CONFIGURATION FOR TURTLEBOT ----------------------
  robot_description = LaunchConfiguration('robot_description')
  # ------------------------------------------------------------------------------

  declare_simulator_cmd = DeclareLaunchArgument(
    name='headless',
    default_value='False',
    description='Whether to execute gzclient')
    
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='true',
    description='Use simulation (Gazebo) clock if true')

  declare_use_simulator_cmd = DeclareLaunchArgument(
    name='use_simulator',
    default_value='True',
    description='Whether to start the simulator')

  declare_world_cmd = DeclareLaunchArgument(
    name='world',
    default_value=world_path,
    description='Full path to the world model file to load')
   
  # ----------------------- NEW DECLARATION FOR TURTLEBOT ----------------------
  declare_robot_description_cmd = DeclareLaunchArgument(
    name='robot_description',
    # XACRO 파일을 읽어 URDF로 변환하는 Command
    default_value=Command(['xacro ', xacro_file_path, ' use_sim_time:=', use_sim_time]),
    description='XACRO path for the robot model'
  )
  # ------------------------------------------------------------------------------
   
  # Specify the actions
  
  # Start Gazebo server
  start_gazebo_server_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
    condition=IfCondition(use_simulator),
    launch_arguments={'world': world}.items())

  # Start Gazebo client    
  start_gazebo_client_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
    condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])))

  # ----------------------- NEW ACTIONS FOR TURTLEBOT -----------------------
  
  # 1. Robot State Publisher: URDF를 읽어 로봇 링크의 TF(트랜스폼)를 발행합니다.
  start_robot_state_publisher_cmd = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    output='screen',
    parameters=[{'use_sim_time': use_sim_time,
                 'robot_description': robot_description}]
  )

  # 2. TurtleBot3 Spawn: 터틀봇 스폰 런치 파일을 포함하여 실행합니다.
  include_turtlebot_spawn_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(spawn_launch_file),
    launch_arguments={
      # TURTLEBOT3_MODEL 환경 변수를 사용하므로, file 인자가 자동으로 처리됩니다.
      'entity_name': 'turtlebot3_waffle',
      'x': '0.0',
      'y': '0.0',
      'z': '0.01'
    }.items() 
  )
  # -------------------------------------------------------------------------

  # Create the launch description and populate
  ld = LaunchDescription()

  # Declare the launch options
  ld.add_action(declare_simulator_cmd)
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_simulator_cmd)
  ld.add_action(declare_world_cmd)
  # ----------------------- NEW DECLARATION -----------------------
  ld.add_action(declare_robot_description_cmd)
  # ---------------------------------------------------------------

  # Add any actions
  ld.add_action(start_gazebo_server_cmd)
  ld.add_action(start_gazebo_client_cmd)
  # ----------------------- NEW ACTIONS -----------------------
  ld.add_action(start_robot_state_publisher_cmd)
  ld.add_action(include_turtlebot_spawn_cmd)
  # -----------------------------------------------------------

  return ld
