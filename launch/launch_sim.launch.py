import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import xacro
from launch.substitutions import LaunchConfiguration, TextSubstitution

def generate_launch_description():

    package_name='urdf_omni_drive'

    # Path to joy config
    joy_config_path = PathJoinSubstitution(
        [FindPackageShare(package_name), "config", "joy.yaml"]
    )

    # Path to rviz2 config
    joy_config_path = PathJoinSubstitution(
        [FindPackageShare(package_name), "config", "view_bot_lidar_map.rviz"]
    )

    # Robot State Publisher
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false'}.items()
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )

    # Spawn robot
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')

    # Joy node (for PS3 input)
    joy_node = Node(package='joy',
             executable='joy_node',
             name='joy_node',
             output='screen'
        )
    
    # Teleop node for converting PS3 input to cmd_vel
    teleop_node = Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            output='screen',
            parameters=[joy_config_path]
        )
    
    slam = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('slam_toolbox'),'launch','online_async_launch.py'
            )]), launch_arguments={'use_sim_time': 'false', 'slam_params_file': './src/urdf_omni_drive/config/mapper_params_online_async.yaml'}.items()
        )
    
    rviz2 = Node(
        package='rviz2',
        namespace='',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', joy_config_path]
    )

    # Robot state publisher for wheel velocities in Rviz2
    xacro_path = os.path.join(get_package_share_directory('urdf_omni_drive'), 'description', 'robot.urdf.xacro')   
    urdf = xacro.process_file(xacro_path)
    robot_state_publisher_node = Node(package='robot_state_publisher',
                                      namespace='',
                                      executable='robot_state_publisher',
                                      parameters=[{'robot_description': urdf.toxml(),
                                                   'use_sim_time': False}])


    # Launch all
    return LaunchDescription([
        rsp,
        # gazebo,
        spawn_entity,
        # joy_node,
        # teleop_node,
        slam,
        rviz2,
        # robot_state_publisher_node
    ])
