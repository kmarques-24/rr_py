import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

# To run:
# Terminal 1: 
#   source install/setup.bash   (redo after build)
#   unset GTK_PATH              (this is needed for some RViz bug)
#   ros2 launch rr_py playback.launch.py 
# Terminal 2:
#   ros2 bag play /home/km/ros2_ws/src/rr_py/bag_files/rr_bag_20260422_173323 --clock --start-paused --loop
#   Or whatever bag file in the arg to run. Second terminal provides playback controls.

def generate_launch_description():
    # bag_path = LaunchConfiguration('bag')

    urdf_path = os.path.join(
        get_package_share_directory('rr_py'), 'urdf', 'rr.urdf.xml')
    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        #DeclareLaunchArgument('bag', description='Path to bag directory'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description,
                         'use_sim_time': True}],
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(
                get_package_share_directory('rr_py'), 'rviz', 'rr.rviz')],
            parameters=[{'use_sim_time': True}],
        ),

        # ExecuteProcess(
        #     cmd=['ros2', 'bag', 'play', bag_path, '--clock'],
        #     output='screen',
        # ),
    ])