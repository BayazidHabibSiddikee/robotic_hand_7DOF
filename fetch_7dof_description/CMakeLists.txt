cmake_minimum_required(VERSION 3.8)
project(fetch_7dof_description)

find_package(ament_cmake REQUIRED)

# Install the robot description, ros2_control configuration, launch
# files, the pick-and-place world and the visual/collision meshes.
install(DIRECTORY
  urdf
  config
  launch
  worlds
  meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
