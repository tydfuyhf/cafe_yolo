import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    # --- 1. Launch Arguments (설정 변수) ---
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # 모델을 'waffle'로 설정 (Launch 파일 내에서만 사용)
    robot_model = 'waffle'
    
    # Path 설정
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_share = get_package_share_directory('two_wheeled_robot')
    pkg_tb3_desc = get_package_share_directory('turtlebot3_description')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    
    # World 파일 경로
    world_file_name = 'cafe.world'
    world_path = os.path.join(pkg_share, 'worlds', world_file_name)

    # 로봇 모델 경로 설정 (GAZEBO_MODEL_PATH 환경 변수)
    custom_models_path = os.path.join(pkg_share, 'two_wheeled_robot', 'models')
    turtlebot3_models_path = os.path.join(pkg_tb3_gazebo, 'models')
    
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ':' + custom_models_path + ':' + turtlebot3_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = custom_models_path + ':' + turtlebot3_models_path

    # URDF 파일 내용 읽기
    # 💡 Waffle 모델의 URDF 파일로 변경
    urdf_file_name = f'turtlebot3_{robot_model}.urdf'
    urdf_path = os.path.join(pkg_tb3_desc, 'urdf', urdf_file_name)
    
    # URDF 파일이 존재하는지 확인 (선택 사항이지만 오류 방지에 도움)
    if not os.path.exists(urdf_path):
        raise FileNotFoundError(f"URDF file not found: {urdf_path}")
        
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    # --- 2. Actions (노드 및 launch 파일 실행) ---
    
    # A. Gazebo 실행
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        # world launch argument는 LaunchConfiguration이 아닌 TextSubstitution으로 직접 전달
        launch_arguments={'world': TextSubstitution(text=world_path)}.items()
    )
    
    # B. Robot State Publisher 실행
    # 'robot_description' 토픽을 발행하여 로봇 구조(TF)를 ROS로 전달합니다.
    # 월드 파일에서 모델을 로드하더라도, 이 노드는 RViz2를 위해 필수입니다.
    start_robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc
        }]
    )

    
    # --- 3. Launch Description 반환 ---
    return LaunchDescription([
        # Launch Argument 선언
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=world_path,
            description='Full path to world file to load'
        ),
        
        # Action 실행
        start_gazebo_cmd,
        start_robot_state_publisher_cmd,
    ])
