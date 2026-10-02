"""Launch the fetch_7dof robot in Gazebo (gz-sim).

Brings up the scene described by the Gymnasium FetchPickAndPlace
environment:

* ``worlds/fetch_table.world``: table with top surface at z = 0.4 m,
  the 5 cm / 2 kg block (object0) and the red target sphere (target0),
  placed as in the MuJoCo model.
* The 7-DOF arm spawned at the environment's fixed base pose
  (x, y, z) = (0.405, 0.48, 0) m.
* Joint states bridged from gz-sim to ROS via ros_gz_bridge.
* Clock synced between gz-sim and ROS.

Usage:
    ros2 launch fetch_7dof_description fetch_7dof_gazebo.launch.py
    ros2 launch fetch_7dof_description fetch_7dof_gazebo.launch.py gui:=false

Requires ROS 2 Jazzy or newer with Gazebo Harmonic (gz-sim):
    sudo apt install ros-<distro>-ros-gz-sim \
        ros-<distro>-gz-ros2-control \
        ros-<distro>-controller-manager ros-<distro>-ros2-controllers \
        ros-<distro>-robot-state-publisher \
        ros-<distro>-ros-gz-bridge
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def _launch_setup(context, *args, **kwargs):
    """Build the gz_args string from resolved launch substitutions."""
    from launch.utilities import perform_substitutions

    pkg_share = FindPackageShare('fetch_7dof_description')
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'fetch_table.world'])

    gui_val = perform_substitutions(context, [LaunchConfiguration('gui')])
    world_val = perform_substitutions(context, [world_file])
    custom_world = perform_substitutions(context, [LaunchConfiguration('world')])
    if custom_world and custom_world != world_val:
        world_val = custom_world

    if gui_val == 'true':
        gz_args_str = f'-r -v 1 {world_val} -g'
    else:
        gz_args_str = f'-r -v 1 {world_val} -s'

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [
                    PathJoinSubstitution(
                        [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py']
                    )
                ]
            ),
            launch_arguments={'gz_args': [gz_args_str]}.items(),
        )
    ]


def generate_launch_description():
    pkg_share = FindPackageShare(package='fetch_7dof_description')

    urdf_file = PathJoinSubstitution([pkg_share, 'urdf', 'fetch_7dof.urdf'])
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'fetch_table.world'])

    # ----------------------------- arguments -----------------------------
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_file,
        description='SDF world to load. Defaults to the pick-and-place scene.',
    )
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Whether to start the Gazebo GUI.',
    )

    # ---------------------------- Gazebo server ----------------------------
    gz_server = OpaqueFunction(function=_launch_setup)

    # -------------------------- robot description --------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': ParameterValue(
                Command(['cat ', urdf_file]), value_type=str
            )
        }],
        output='screen',
    )

    # Spawn the arm at the Gymnasium environment's fixed base pose.
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'fetch_7dof',
            '-x', '0.405',
            '-y', '0.48',
            '-z', '0.0',
        ],
    )

    # ----------------------- gz-sim <-> ROS bridge -------------------------
    # Bridge clock and joint states from gz-sim to ROS 2.
    # The URDF's JointStatePublisher plugin publishes on:
    #   /world/<name>/model/<robot_name>/joint_state (gz.msgs.Model)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/world/fetch_pick_and_place/model/fetch_7dof/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[
            ('/world/fetch_pick_and_place/model/fetch_7dof/joint_state',
             'joint_states'),
        ],
        output='screen',
    )

    return LaunchDescription([
        world_arg,
        gui_arg,
        gz_server,
        robot_state_publisher,
        spawn_entity,
        bridge,
    ])
