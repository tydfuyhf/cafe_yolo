import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    robot_model = 'waffle'

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_share = get_package_share_directory('two_wheeled_robot')
    pkg_tb3_desc = get_package_share_directory('turtlebot3_description')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    world_path = os.path.join(pkg_share, 'worlds', 'cafe.world')
    weights_path = os.path.join(pkg_share, 'weights', 'yolov8m.pt')

    custom_models_path = os.path.join(pkg_share, 'models')
    turtlebot3_models_path = os.path.join(pkg_tb3_gazebo, 'models')

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ':' + custom_models_path + ':' + turtlebot3_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = custom_models_path + ':' + turtlebot3_models_path

    urdf_path = os.path.join(pkg_tb3_desc, 'urdf', f'turtlebot3_{robot_model}.urdf')
    if not os.path.exists(urdf_path):
        raise FileNotFoundError(f'URDF not found: {urdf_path}')
    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    start_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': TextSubstitution(text=world_path)}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc,
        }]
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', f'turtlebot3_{robot_model}',
            '-topic', 'robot_description',
            '-x', '-2.0', '-y', '0.0', '-z', '0.1', '-Y', '1.57',
        ],
        output='screen',
    )

    yolo_node = Node(
        package='yolo_ros',
        executable='yolo_node',
        name='yolo_detector',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'model': weights_path,
            'device': 'cpu',
            'threshold': 0.5,
        }],
        remappings=[('image_raw', '/camera/rgb/image_raw')],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),
        start_gazebo,
        robot_state_publisher,
        spawn_robot,
        yolo_node,
    ])
