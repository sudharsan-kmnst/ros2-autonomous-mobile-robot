from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node

spawn_delay = 5.0  # seconds to wait for Gazebo to finish loading the world

def generate_launch_description():
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_my_bot',
        output='screen',
        arguments=['-topic', 'robot_description', '-name', 'my_bot', '-z', '0.1'],
    )
    return LaunchDescription([
        TimerAction(period=spawn_delay, actions=[spawn_robot]),
    ])