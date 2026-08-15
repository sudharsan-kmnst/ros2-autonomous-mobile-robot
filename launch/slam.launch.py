import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import TimerAction, ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    params = os.path.join(
        get_package_share_directory('my_bot'),
        'config', 'mapper_params_online_async.yaml')

    # SLAM node — comes up unconfigured
    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[params, {'use_sim_time': True}],
    )

    # the two lifecycle transitions, as clean argument lists (no shell, no quoting)
    configure = ExecuteProcess(
        cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'configure'],
        output='screen')
    activate = ExecuteProcess(
        cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'activate'],
        output='screen')

    return LaunchDescription([
        slam,
        TimerAction(period=10.0, actions=[configure]),   # wait for node + sim
        TimerAction(period=13.0, actions=[activate]),
    ])