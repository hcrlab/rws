. ~/.bashrc

# sourcing catkin_ws/devel/setup.bash causes rosbridge_server to not be able to launch.
# Preprending ~/catkin_ws/devel to this environment variable is the culprit for some reason.
export CMAKE_PREFIX_PATH='/opt/ros/groovy'
roslaunch rws rws.launch
