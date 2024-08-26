import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,
                            Shutdown)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import yaml
from moveit_configs_utils import MoveItConfigsBuilder

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    robot_ip_parameter_name = 'robot_ip'
    use_fake_hardware_parameter_name = 'use_fake_hardware'
    load_gripper_parameter_name = 'load_gripper'
    fake_sensor_commands_parameter_name = 'fake_sensor_commands'

    robot_ip = LaunchConfiguration(robot_ip_parameter_name)
    use_fake_hardware = LaunchConfiguration(use_fake_hardware_parameter_name)
    load_gripper = LaunchConfiguration(load_gripper_parameter_name)
    fake_sensor_commands = LaunchConfiguration(fake_sensor_commands_parameter_name)
    franka_xacro_file = os.path.join(get_package_share_directory('franka_description'), 'robots',
                                     'panda_arm.urdf.xacro')    
    moveit_config = (
        MoveItConfigsBuilder("pd")
        .robot_description(
            file_path=franka_xacro_file,
            mappings={
                "hand": LaunchConfiguration('load_gripper'),
                "robot_ip": LaunchConfiguration('robot_ip'),
                "use_fake_hardware": LaunchConfiguration('use_fake_hardware'),
                "fake_sensor_commands": LaunchConfiguration('fake_sensor_commands')
            }
        )
        .to_moveit_configs()
    )
    robot_arg = DeclareLaunchArgument(
        robot_ip_parameter_name,
        default_value='192.168.101.116',
        description='Hostname or IP address of the robot.')

    use_fake_hardware_arg = DeclareLaunchArgument(
        use_fake_hardware_parameter_name,
        default_value='false',
        description='Use fake hardware')


   
    fake_sensor_commands_arg = DeclareLaunchArgument(
        fake_sensor_commands_parameter_name,
        default_value='false',
        description="Fake sensor commands. Only valid when '{}' is true".format(
            use_fake_hardware_parameter_name))
    load_gripper_arg = DeclareLaunchArgument(
        'load_gripper',
        default_value='true',
        description='Use Franka Gripper as an end-effector, otherwise, the robot is loaded without an end-effector.'
    )

    # Get the launch configuration for the gripper
    load_gripper = LaunchConfiguration('load_gripper')

    # Include the gripper launch file conditionally
    gripper_launch_file = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
            [FindPackageShare('franka_gripper'), 'launch', 'gripper.launch.py'])]),
        launch_arguments={
            'robot_ip': LaunchConfiguration('robot_ip'),
            'use_fake_hardware': LaunchConfiguration('use_fake_hardware')
        }.items(),
        condition=IfCondition(load_gripper)  # Only include if load_gripper is true
    )
    node = Node(
        package="franka_tc",
        executable="cartesian",
        output="screen",
        parameters=[
            robot_arg,
            use_fake_hardware_arg,
            load_gripper_arg,
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            moveit_config.planning_pipelines,
        ],
    )

    return LaunchDescription([node])
