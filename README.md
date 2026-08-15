# Autonomous Mobile Robot — SLAM + Nav2 (ROS 2 Jazzy · Gazebo Harmonic)

A differential-drive mobile robot, modeled from scratch, that **builds a map of an unknown environment with SLAM and then navigates it autonomously** using the Nav2 stack — localizing with AMCL and following paths with an MPPI (sampling-based MPC) controller.

Built end-to-end in **ROS 2 Jazzy** + **Gazebo Harmonic**.

<!-- Add your recording here -->
![Demo: autonomous navigation to a goal](docs/demo.gif)

---

## What it does

1. **Robot description** — a differential-drive robot defined in URDF/Xacro (chassis, two drive wheels, caster, 2D lidar) with correct inertials and TF frames.
2. **Simulation** — spawned in Gazebo Harmonic; sensors and motors bridged to ROS 2 via `ros_gz_bridge`.
3. **Mapping (SLAM)** — `slam_toolbox` builds an occupancy-grid map while driving with teleop, then the map is saved.
4. **Autonomous navigation (Nav2)** — `map_server` loads the saved map, **AMCL** localizes the robot (particle filter), and **Nav2** plans a global path and drives to a goal, avoiding obstacles, using an **MPPI** local controller.

---

## Tech stack

| Layer | Tool |
|---|---|
| Middleware | ROS 2 Jazzy |
| Simulator | Gazebo Harmonic (`gz-sim`) |
| Sim ↔ ROS | `ros_gz_bridge`, `gz::sim::systems::DiffDrive` |
| Robot model | URDF / Xacro |
| Mapping | `slam_toolbox` (online async) |
| Localization | `nav2_amcl` |
| Navigation | Nav2 (planner, MPPI controller, costmaps, BT navigator) |
| Visualization | RViz2 |

---

## System architecture

The whole system is a pipeline of coordinate transforms (TF). The frame tree:

```
map ──> odom ──> base_footprint ──> base_link ──> lidar_link
 │        │             │                │
SLAM/   Diff-        (fixed)       robot_state_publisher
AMCL    Drive
```

- `map → odom` — the drift correction, published by **SLAM** (while mapping) or **AMCL** (while navigating).
- `odom → base_footprint` — wheel odometry from the DiffDrive plugin (smooth, drifts).
- `base_footprint → base_link → lidar_link` — the robot body, from `robot_state_publisher`.

`base_link` sits at the **drive axle** (the instantaneous center of rotation), so wheel odometry integrates exactly there.

---

## Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- `ros-jazzy-slam-toolbox`, `ros-jazzy-nav2-bringup`, `ros-jazzy-ros-gz`, `ros-jazzy-teleop-twist-keyboard`

---

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select my_bot --symlink-install
source install/setup.bash
```

---

## Usage

### 1. Build a map (SLAM)

```bash
# Terminal 1 — simulation
ros2 launch my_bot gazebo.launch.xml

# Terminal 2 — SLAM (auto-activates the lifecycle node)
ros2 launch my_bot slam.launch.py

# Terminal 3 — drive around to build the map
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Watch the map form in RViz (Fixed Frame `map`, add a **Map** display on `/map`). When it's complete, save it:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/my_bot/maps/my_world
```

This writes `my_world.pgm` (grid) + `my_world.yaml` (metadata).

### 2. Navigate autonomously (Nav2 + AMCL)

```bash
# Terminal 1 — simulation (no SLAM this time)
ros2 launch my_bot gazebo.launch.xml

# Terminal 2 — Nav2 stack (map_server + AMCL + planner + controller)
ros2 launch my_bot navigation.launch.xml

# Terminal 3 — RViz
ros2 run rviz2 rviz2 -d /opt/ros/jazzy/share/nav2_bringup/rviz/nav2_default_view.rviz \
  --ros-args -p use_sim_time:=true
```

In RViz:
1. **2D Pose Estimate** — click the robot's location and drag its heading (seeds AMCL).
2. Drive briefly with teleop so the particle cloud converges.
3. **Nav2 Goal** — click a destination; the robot plans a path and drives there, avoiding obstacles.

> Note: use only the RViz toolbar tools. Nav2's lifecycle is auto-started — don't click the Startup/Reset/Pause panel buttons.

---

## Project structure

```
my_bot/
├── urdf/                 # robot description (Xacro)
│   ├── robot_core.xacro          # links, joints, frames
│   ├── lidar.xacro               # lidar link + gpu_lidar sensor
│   ├── gazebo_control.xacro      # DiffDrive + joint-state plugins
│   └── inertial_macros.xacro     # reusable inertia math
├── launch/
│   ├── rsp.launch.xml            # robot_state_publisher
│   ├── gazebo.launch.xml         # sim + spawn + bridge
│   ├── slam.launch.py            # SLAM + lifecycle auto-activation
│   └── navigation.launch.xml     # Nav2 bringup
├── config/
│   ├── gz_bridge.yaml            # ros_gz topic bridge
│   ├── mapper_params_online_async.yaml   # slam_toolbox params
│   └── nav2_params.yaml          # Nav2 params
├── worlds/               # Gazebo world
└── maps/                 # saved map (.pgm + .yaml)
```

---

## Engineering challenges solved

A few of the real bugs debugged along the way (and what they taught):

- **Robot spun instead of driving** — the two wheel joints had opposite spin axes; the DiffDrive plugin assumes both share axis orientation. Flipped one wheel's axis.
- **`base_footprint` dropped from TF** — publishing odometry to `base_link` gave it two parents; a TF frame can have only one. Fixed the `child_frame_id`.
- **SLAM ran but did nothing** — `slam_toolbox` is a lifecycle node; it's inert until `configure`+`activate`. Automated the transition in the launch.
- **Robot tipped over** — the center of mass sat on the edge of the support polygon; shifted the chassis mass forward.
- **XML launch failed to load the URDF** — a colon inside a URDF comment broke YAML type-inference in the `<param>` value.

---

## Roadmap

- [ ] Port to real hardware (`ros2_control` hardware interface + RPLIDAR + IMU + EKF sensor fusion)
- [ ] Tune the MPPI controller and costmap inflation for tighter navigation
- [ ] Add multi-goal / waypoint following

---

## Acknowledgements

Built on the open-source ROS 2, `slam_toolbox`, and Nav2 projects.
