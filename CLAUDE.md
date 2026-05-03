# cafe_yolo — CLAUDE.md

## 프로젝트 개요

TurtleBot3 Waffle에 YOLOv8을 올려 **Gazebo 카페 월드 안에서 사람을 감지하고 회피**하는 ROS 2 시뮬레이션 프로젝트.

- **타겟 환경**: ROS 2 Humble + Gazebo Classic (Ubuntu 22.04)
- **용도**: 첫 포트폴리오용 프로젝트. 실행 화면은 repo 루트의 `cafe_yolo.png` 참고.
- **현재 시스템**: Ubuntu 24.04 + ROS Jazzy (개발 머신). 코드는 Humble 기준으로 작성.

---

## 패키지 구조

```
src/
├── yolo_msgs/          # 커스텀 ROS2 메시지 12종 (Detection, BBox2D/3D, KeyPoint 등)
├── yolo_ros/           # YOLO 추론 노드 4개 (yolo_node, detect_3d_node, tracking_node, debug_node)
├── yolo_bringup/       # launch 파일 (yolo.launch.py 본체 + yolov8.launch.py 래퍼)
└── two_wheeled_robot/  # TurtleBot3 Gazebo 시뮬 패키지 (카페 월드, 모델, 가중치)
```

### 진입점

```bash
ros2 launch two_wheeled_robot cafe_turtlebot3.launch.py
```

---

## 의존성

### 외부 ROS 패키지 (Humble)
- `gazebo_ros` — Gazebo Classic 브릿지
- `turtlebot3_description` — TurtleBot3 URDF
- `turtlebot3_gazebo` — TurtleBot3 Gazebo 모델/spawn
- `robot_state_publisher`, `joint_state_publisher`
- `rviz2`, `xacro`

### Python
- `ultralytics` (YOLOv8, AGPL-3.0)
- `torch`, `opencv-python`, `numpy`
- `cv_bridge`

---

## YOLO 관련 라이선스

이 프로젝트는 [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)을 사용하며,
해당 라이브러리는 **AGPL-3.0** 라이선스를 따릅니다.
`yolo_ros`, `yolo_msgs`, `yolo_bringup` 패키지 원본은 Miguel Ángel González Santamarta가 작성한 GPL-3 코드 기반입니다.

---

## 현재 구현 상태

### 완성된 부분
- [x] YOLO 추론 파이프라인 (2D 탐지 → 3D 변환 → 추적 → 시각화)
- [x] Gazebo 카페 월드 (걸어다니는 actor 2명 포함)
- [x] TurtleBot3 Waffle 모델 스폰
- [x] 커스텀 ROS2 메시지 정의 12종

### 미완성 — 추후 구현 필요
- [ ] **사람 회피 컨트롤러 노드** (핵심 미구현)
  - `DetectionArray` 구독 → 3D bbox에서 사람 거리 계산 → `/cmd_vel` 발행
  - 로직: 사람이 N미터 이내 진입 시 정지/방향 전환
  - 패키지: `two_wheeled_robot` 안에 `person_avoidance_node.py` 추가 예정
- [ ] **Nav2 연동** (선택사항)
  - 단순 반응형 회피 대신 경로 계획 기반 회피로 업그레이드
- [ ] **Gazebo Harmonic 포팅** (현재 개발 머신이 Jazzy라 필요시)
  - `gazebo_ros` → `ros_gz_sim`
  - `libActorPlugin.so` → SDF script 방식 actor
  - turtlebot3_waffle model.sdf 플러그인 교체

---

## 코드 정리 이력 (2025-05-03)

- `yolo_bringup/launch/` 에서 사용하지 않는 버전 래퍼 삭제: yolov5/9/10/11/12/yolo-world/yoloe
- 참조 파일 없는 런치 파일 삭제: `empty_cafe.launch.py`, `load_world_into_gazebo.launch.py`, `two_wheeled_robot_rviz.launch.py`
- `two_wheeled_robot/package.xml` 수정: `rviz` → `rviz2`
- `cafe_turtlebot3.launch.py` 주석 정리
- `LICENSE` 추가 (AGPL-3.0)
- `README.md` 작성

---

## 노트

- `two_wheeled_robot/weights/yolov8m.pt` — 가중치 파일 (50MB), `.gitignore`에 추가 고려
- `cafe.world`의 actor는 Gazebo Classic `libActorPlugin.so` 사용 — Humble 환경에서는 정상 작동
- YOLO 노드 기본 디바이스: `cpu` (launch 파일에서 변경 가능)
