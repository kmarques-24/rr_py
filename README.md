# ROS2 2D occupancy grid mapper for RESCUE Roller.
## Overview
1. Roller receives arrow key commands (/cmd_vel) from keyboard
2. Roller publishes odometry data (/odom) and ToF sensor data (/points)
3. ToF sensor data is converted to laserscan data (/scan) for use with slam_toolbox to make a 2D map
4. State publisher provides static robot description from .urdf file so roller can be visualized
5. Odometry broadcaster publishes dynamic transform for slam_toolbox from odometry data (roller in world frame)
6. slam_toolbox generates map (/map)
7. Bag file is saved to rr_py/bag_files for later playback

## Requirements
* Ubuntu 22.04
* ROS 2 Humble
* Python 3.10
* Workspace ~/ros2_ws 

# Partner Repository
Meant for use with: https://github.com/kmarques-24/RR

## Getting Started
Configure ROS 2 environment: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html

In ~/ros2_ws, run the following to start working in VScode:
```
source /opt/ros/humble/setup.bash
source install/setup.bash
code .
```

If not already installed, install the following packages:
```
sudo apt install ros-humble-slam-toolbox
sudo apt install ros-humble-pointcloud-to-laserscan
sudo apt install ros-humble-robot-state-publisher
sudo apt install ros-humble-tf2-ros
sudo apt install ros-humble-rviz2
```

Clone the rr_py package by running the following command in ~/ros2_ws/src:
```
git clone https://github.com/IceCreamSandwhich/RR.git
```

# Router
Plug in router and wait a minute for network RR to become visible. 

Connect and open http://192.168.8.1/ to see connected clients (laptop, esp32) and IPs.

## Building and Developing
Git commands should be run from ~/ros2_ws/src/rr_py.

Always return to ~/ros2_ws before building:
```
colcon build --packages-select rr_py
source install/setup.bash
```

## Real-Time Mapping
All terminals should be opened from ~/ros2_ws.

### Instructions
1. Set up Terminal 1. 
2. Turn the RESCUE Roller on. Hit the hardware reset. Roller should now be publishing data.
3. Set up Terminals 2 & 3. 
4. Teleoperate robot and watch map generate.
5. Close the map and end the bag recording with Ctrl+C. 

### Terminal 1
Run the following to start the micro-ROS agent:
```
sudo docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
```
Verbosity flag -v6 can be lowered if desired.

### Terminal 2
Run the following to teleoperate the RESCUE Roller:
```
run ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Terminal 3
Run the following to launch the real time mapper:
```
source install/setup.bash
unset GTK_PATH              
ros2 launch rr_py rr.launch.py 
```
It's always good practice to source install/setup.bash to catch latest build.  
The unset GTK_PATH line is needed to resolve a conflict with RViz.  
rr.launch.py starts a bag recording and creates the following nodes:  
* robot_state_publisher to publish static transforms from rr.urdf
* pointcloud_to_laserscan to convert data from /points to /scan for slam_toolbox
* odom_tf_broadcaster to publish dynamic transform of robot body (base_link) in world frame (odom)
* slam_toolbox to generate map from /odom and /scan
* rviz to visualize robot in map

## Playback Mapping
All terminals should be opened from ~/ros2_ws.

### Instructions
1. Set up Terminals 1 & 2. 
2. Press space in Terminal 1 to start playback.

### Terminal 1
Run the following to play the desired bag data:
```
ros2 bag play /home/km/ros2_ws/src/rr_py/bag_files/<bag file> --clock --start-paused --loop
```
This terminal provides playback controls.

### Terminal 2
Run the following to launch the playback mapper:
```
source install/setup.bash
unset GTK_PATH              
ros2 launch rr_py playback.launch.py 
```
This publish static transforms from rr.urdf and starts RViz. 

