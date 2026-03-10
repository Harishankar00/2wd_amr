cmake_minimum_required(VERSION 3.8)
project(amr)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install all resource directories so they are accessible at runtime
install(
  DIRECTORY
    launch
    description
    world
    config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
