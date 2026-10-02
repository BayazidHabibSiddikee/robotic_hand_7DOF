"""Launch the fetch_7dof robot in Gazebo (gz-sim).

Brings up the scene described by the Gymnasium FetchPickAndPlace
environment:

* ``worlds/fetch_table.world``: table with top surface at z = 0.4 m,
  the 5 cm / 2 kg block (object0) and the red target sphere (target0),
  placed as in the MuJoCo model.
* The 7-DOF arm spawned at the environment's fixed base pose
  (x, y, z) = (0.405, 0.48, 0) m.
* ros2_control running at 25 Hz (the env's control frequency: one
  action held for 20 substeps of dt = 0.002 s) with a
  joint_state_broadcaster plus separate arm and gripper
  JointTrajectoryControllers.

Usage:
    ros2 launch fetch_7dof_description fetch_7dof_gazebo.launch.py
    ros2 launch fetch_7dof_description fetch_7dof_gazebo.launch.py gui:=false

Requires ROS 2 Jazzy or newer with Gazebo Harmonic (gz-sim):
    sudo apt install ros-<distro>-ros-gz \
        ros-<distro>-gz-ros2-control \
        ros-<distro>-controller-manager ros-<distro>-ros2-controllers \
        ros-<distro>-robot-state-publisher
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package='fetch_7dof_description')

    urdf_file = PathJoinSubstitution([pkg_share, 'urdf', 'fetch_7dof.urdf'])
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'fetch_table.world'])
    ros2_control_file = PathJoinSubstitution(
        [pkg_share, 'config', 'ros2_control.yaml']
    )

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
    # gz_args string passed to gz_sim.launch.py: includes verbose flag,
    # the world file, and -g for GUI (or -s for server-only).
    gz_args_default = [
        '-r -v 1 ', world_file,
        ' -g'
    ]
    gz_args_arg = DeclareLaunchArgument(
        'gz_args',
        default_value=gz_args_default,
        description='Arguments passed to gz sim (world + GUI flag).',
    )

    # ---------------------------- Gazebo server ----------------------------
    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                PathJoinSubstitution(
                    [FindPackageShare('ros_gz'), 'launch', 'gz_sim.launch.py']
                )
            ]
        ),
        launch_arguments={
            'gz_args': [LaunchConfiguration('gz_args')]
        }.items(),
    )

    # -------------------------- robot description --------------------------
    # robot_state_publisher publishes the URDF as TF and republishes it on
    # the /robot_description topic, which gz_spawn_entity create subscribes to.
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['cat ', urdf_file])}],
        output='screen',
    )

    # Spawn the arm at the Gymnasium environment's fixed base pose.
    # Uses gz-sim's spawn_entity (ros-gz-spawn-entity) to create the robot
    # from the URDF loaded on the /robot_description topic.
    spawn_entity = Node(
        package='gz_spawn_entity',
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

    # ----------------------------- ros2_control -----------------------------
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[ros2_control_file],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )
    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_joint_trajectory_controller'],
        output='screen',
    )
    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_joint_trajectory_controller'],
        output='screen',
    )

    return LaunchDescription([
        world_arg,
        gui_arg,
        gz_args_arg,
        gz_server,
        robot_state_publisher,
        spawn_entity,
        controller_manager,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        gripper_controller_spawner,
    ])
