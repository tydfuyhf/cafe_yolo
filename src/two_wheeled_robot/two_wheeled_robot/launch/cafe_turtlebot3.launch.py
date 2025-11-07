# cafe_turtlebot3.launch.py
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
    robot_model = 'waffle'
    
    # Path 설정
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_share = get_package_share_directory('two_wheeled_robot')
    pkg_tb3_desc = get_package_share_directory('turtlebot3_description')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    
    # World 파일 경로
    world_file_name = 'cafe.world'
    world_path = os.path.join(pkg_share, 'worlds', world_file_name)

    # 💡 [추가] YOLO 가중치 파일 경로 설정
    weights_file_name = 'yolov8m.pt'
    weights_path = os.path.join(pkg_share, 'weights', weights_file_name)

    # 로봇 모델 경로 설정 (GAZEBO_MODEL_PATH 환경 변수)
    # [수정] custom_models_path 경로 수정 (이전 코드에 'two_wheeled_robot'이 중복되어 있었음)
    custom_models_path = os.path.join(pkg_share, 'models') 
    turtlebot3_models_path = os.path.join(pkg_tb3_gazebo, 'models')
    
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ':' + custom_models_path + ':' + turtlebot3_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = custom_models_path + ':' + turtlebot3_models_path

    # URDF 파일 내용 읽기
    urdf_file_name = f'turtlebot3_{robot_model}.urdf'
    urdf_path = os.path.join(pkg_tb3_desc, 'urdf', urdf_file_name)
    
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
        launch_arguments={'world': TextSubstitution(text=world_path)}.items()
    )
    
    # B. Robot State Publisher 실행
    start_robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_desc
        }]
    )

    # 💡 C. YOLO 탐지 노드 추가 (정확한 실행 파일 이름 사용: yolo_node)
    yolo_detector_node = Node(
        package='yolo_ros',
        executable='yolo_node', # <--- 확인된 실행 파일 이름
        name='yolo_detector',
        output='screen', # <--- 로그 메시지를 터미널에 띄우기 위한 설정
        parameters=[{
            'use_sim_time': use_sim_time,
            'device': 'cpu',
            # 💡 [수정] 가중치 파일 경로 파라미터로 전달
            'model': weights_path  
        }],
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
        yolo_detector_node, # <--- YOLO 탐지 노드 추가
    ])
