cmake_minimum_required(VERSION 3.8)
project(my_bot)

find_package(ament_cmake REQUIRED)

# Install the resource directories so ros2 launch / xacro can find them via
# get_package_share_directory('my_bot'). Add config/ and worlds/ now so Days 2-4
# drop straight in without touching this file again.
install(
  DIRECTORY urdf launch config worlds maps
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
