import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from datetime import datetime

# To run:
# Terminal 1: 
#   sudo docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
# Terminal 2: 
#   source install/setup.bash   (redo after build)
#   unset GTK_PATH              (this is needed for some RViz bug)
#   ros2 launch rr_py rr.launch.py 
#   Optional arg: use_rviz:=false

def generate_launch_description():

    bag_dir = os.path.expanduser('~/ros2_ws/src/rr_py/bag_files')
    os.makedirs(bag_dir, exist_ok=True) # create if not already there
    bag_name = f'rr_bag_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    bag_path = os.path.join(bag_dir, bag_name)

    use_rviz   = LaunchConfiguration('use_rviz')
    
    urdf_path = os.path.join(
        get_package_share_directory('rr_py'), 'urdf', 'rr.urdf.xml')

    with open(urdf_path, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([

        # ----- Arguments -----
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for visualization'
        ),

        # ----- Static transforms -----
        # inside generate_launch_description():
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),

        # ----- PointCloud2 to LaserScan -----
        # slam_toolbox requires LaserScan, not PointCloud2
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan',
            remappings=[
                ('cloud_in', '/points'),
                ('scan',     '/scan')
            ],
            parameters=[{
                'target_frame':    'tof_link',
                'min_height':      -0.5,
                'max_height':       0.5,
                'angle_min':       -0.4232,
                'angle_max':        0.4232,
                'angle_increment':  0.12091,  # 0.8464 / 8 = 0.1058, gives exactly 8 beams
                'range_min':        0.05,
                'range_max':        1.0,
                'use_inf':          True,
            }]
        ),
        # ----- Broadcast odom transform -----
        # slam_toolbox uses tf2, so need to take from /odom and publish here
        Node(
            package='rr_py',
            executable='odom_tf_broadcaster',
            name='odom_tf_broadcaster',
            output='screen'
        ),

        # ----- Topic sentinel -----
        # Exits cleanly once /scan and /points both have data.
        # OnProcessExit below uses this as the trigger.
        (topic_waiter := ExecuteProcess(
            cmd=['ros2', 'run', 'rr_py', 'topic_waiter'],
            output='screen'
        )),

        # ----- Event-driven: start SLAM and bag when sentinel exits -----
        RegisterEventHandler(
            OnProcessExit(
                target_action=topic_waiter,
                on_exit=[

                    Node(
                        package='slam_toolbox',
                        executable='async_slam_toolbox_node',
                        name='slam_toolbox',
                        output='screen',
                        parameters=[{
                            'use_sim_time':            False,
                            'odom_frame':              'odom',
                            'base_frame':              'base_link',
                            'map_frame':               'map',
                            'scan_topic':              '/scan',
                            'mode':                    'mapping',
                            'resolution':               0.05,
                            'min_laser_range':          0.02,
                            'max_laser_range':          1.0,
                            'minimum_travel_distance':  0.05,
                            'minimum_travel_heading':   0.1,
                            'transform_publish_period': 0.02,  # 50 Hz tf update
                            'tf_buffer_duration':       10.0,  # keep 30s of tf history (default is 30s anyway)
                            'map_update_interval':      1.0,   # lower = more responsive
                            'use_scan_matching':        False,
                            # 'use_scan_matching':        True,  # default true. Will correct pose based on map 
                            # 'correlation_search_space_dimension':         0.1,   # smaller = trust odom more
                            # 'correlation_search_space_resolution':        0.01,
                            # 'correlation_search_space_smear_deviation':   0.02,   # safely under dimension/4 
                            #     # scan matcher only searches this size square. Prevents scan matcher from
                            #     # correcting pose too aggressively. Lower value trusts odom more
                            # 'link_match_minimum_response_fine':           0.3,    # Accept scans with weaker match quality
                            # 'do_loop_closing':                            False,  # Disable loop closure during debugging
                        }]
                    ),

                    ExecuteProcess(
                        cmd=[
                            'ros2', 'bag', 'record',
                            '-o', bag_path,
                            '/points',
                            '/odom',
                            '/imu/data',
                            '/scan',
                            '/map',
                            '/tf',
                            '/tf_static',
                            '/robot_description',
                        ],
                        output='screen'
                    ),

                ]
            )
        ),

        # ----- RViz -----
        Node(
            package='rviz2',
            executable='rviz2',
            condition=IfCondition(use_rviz),
            arguments=['-d', os.path.join(
                get_package_share_directory('rr_py'), 'rviz', 'rr.rviz')],
            output='screen'
        ),

    ])