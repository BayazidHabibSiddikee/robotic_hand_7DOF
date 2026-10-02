from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.utilities import perform_substitutions

def _launch_setup(context, *args, **kwargs):
    pkg_share = FindPackageShare('fetch_7dof_description')
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'fetch_table.world'])
    world_val = perform_substitutions(context, [world_file])
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
            ]),
            launch_arguments={'gz_args': [f'-r -v 1 {world_val} -s']}.items(),
        )
    ]

def generate_launch_description():
    pkg_share = FindPackageShare(package='fetch_7dof_description')
    urdf_file = PathJoinSubstitution([pkg_share, 'urdf', 'fetch_7dof.urdf'])
    return LaunchDescription([
        OpaqueFunction(function=_launch_setup),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': ParameterValue(Command(['cat ', urdf_file]), value_type=str)}],
            output='screen',
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            output='screen',
            arguments=['-topic', 'robot_description', '-name', 'fetch_7dof', '-x', '0.405', '-y', '0.48', '-z', '0.0'],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/world/fetch_pick_and_place/model/fetch_7dof/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            remappings=[('/world/fetch_pick_and_place/model/fetch_7dof/joint_state', 'joint_states')],
            output='screen',
        ),
    ])
