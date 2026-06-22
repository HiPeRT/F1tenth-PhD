import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    follow_the_gap_dir = get_package_share_directory('follow_the_gap')
    config_file = os.path.join(follow_the_gap_dir, 'config', 'config.yaml')
    
    return LaunchDescription([
        Node(
            package='follow_the_gap',
            executable='follow_the_gap',
            name='FollowGap_node',
            output='screen',
            emulate_tty=True,
            parameters=[config_file],
        ),
    ])