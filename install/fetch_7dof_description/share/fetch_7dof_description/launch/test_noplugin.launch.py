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
    gz_args_str = f'-r -v 1 {world_val} -s'
    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
            ]),
            launch_arguments={'gz_args': [gz_args_str]}.items(),
        )
    ]

def generate_launch_description():
    pkg_share = FindPackageShare(package='fetch_7dof_description')
    # Use a simplified URDF without gz_ros2_control plugin
    urdf_no_plugin = '''<?xml version="1.0"?>
<robot name="fetch_test">
  <link name="base_link">
    <inertial><origin xyz="0 0 0"/><mass value="1"/><inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/></inertial>
    <visual><geometry><box size="0.1 0.1 0.1"/></geometry></visual>
  </link>
  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <origin xyz="0 0 0.1"/>
    <axis xyz="0 1 0"/>
    <limit effort="10" lower="-3.14" upper="3.14" velocity="1"/>
  </joint>
  <link name="link1">
    <inertial><origin xyz="0 0 0"/><mass value="1"/><inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/></inertial>
    <visual><geometry><box size="0.05 0.05 0.2"/></geometry></visual>
  </link>
</robot>'''
    
    return LaunchDescription([
        OpaqueFunction(function=_launch_setup),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': urdf_no_plugin}],
            output='screen',
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            output='screen',
            arguments=['-topic', 'robot_description', '-name', 'test_robot', '-x', '0', '-y', '0', '-z', '0'],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/world/test/world@test/model/test_robot/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            remappings=[('/world/test/world@test/model/test_robot/joint_state', 'joint_states')],
            output='screen',
        ),
    ])
