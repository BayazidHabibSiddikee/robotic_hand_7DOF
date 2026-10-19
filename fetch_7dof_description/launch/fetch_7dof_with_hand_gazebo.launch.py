"""Launch the Fetch arm + 7-DOF FreeCAD hand in Gazebo (gz-sim).

Same pick-and-place scene as fetch_7dof_gazebo.launch.py, but the robot
description is the combined arm+hand URDF
(freecad_hand_7dof/urdf/fetch_7dof_with_hand.urdf): stock 2-finger
gripper_link replaced by the 7-DOF hand (H1..H7). The extra
hand_joint_trajectory_controller (see config/ros2_control.yaml) drives
H1..H7; arm/gripper controllers are unchanged.

Usage:
    ros2 launch fetch_7dof_description fetch_7dof_with_hand_gazebo.launch.py
    ros2 launch fetch_7dof_description fetch_7dof_with_hand_gazebo.launch.py gui:=false
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def _launch_setup(context, *args, **kwargs):
    from launch.utilities import perform_substitutions

    pkg_share = FindPackageShare('fetch_7dof_description')
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'fetch_table.world'])

    gui_val = perform_substitutions(context, [LaunchConfiguration('gui')])
    world_val = perform_substitutions(context, [world_file])
    custom_world = perform_substitutions(context, [LaunchConfiguration('world')])
    if custom_world and custom_world != world_val:
        world_val = custom_world

    gz_args_str = f'-r -v 1 {world_val} -g' if gui_val == 'true' else f'-r -v 1 {world_val} -s'
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]
            ),
            launch_arguments={'gz_args': [gz_args_str]}.items(),
        )
    ]


def generate_launch_description():
    pkg_share = FindPackageShare(package='fetch_7dof_description')

    # Combined arm + 7-DOF hand URDF.
    urdf_file = PathJoinSubstitution(
        [pkg_share, '..', 'freecad_hand_7dof', 'urdf', 'fetch_7dof_with_hand.urdf'])
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'fetch_table.world'])

    world_arg = DeclareLaunchArgument('world', default_value=world_file,
        description='SDF world to load. Defaults to the pick-and-place scene.')
    gui_arg = DeclareLaunchArgument('gui', default_value='true',
        description='Whether to start the Gazebo GUI.')
    gz_server = OpaqueFunction(function=_launch_setup)

    robot_state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'robot_description': ParameterValue(Command(['cat ', urdf_file]), value_type=str)}],
        output='screen',
    )
    spawn_entity = Node(
        package='ros_gz_sim', executable='create', output='screen',
        arguments=['-topic', 'robot_description', '-name', 'fetch_7dof_hand',
                   '-x', '0.405', '-y', '0.48', '-z', '0.0'],
    )
    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/world/fetch_pick_and_place/model/fetch_7dof_hand/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[('/world/fetch_pick_and_place/model/fetch_7dof_hand/joint_state', 'joint_states')],
        output='screen',
    )
    return LaunchDescription([world_arg, gui_arg, gz_server,
                              robot_state_publisher, spawn_entity, bridge])
