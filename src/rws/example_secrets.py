# The Google Client ID for your application, used for Google Sign-in.
# See https://developers.google.com/identity/sign-in/web/devconsole-project
GOOGLE_CLIENT_ID = '1234-abcd.apps.googleusercontent.com'

# A launch file to bring up the robot with.
BRINGUP_FILE = '/home/rosie/bringup.launch'

# The catkin workspace to load apps from.
CATKIN_WS = '/home/rosie/rws/catkin_ws'

# When developing, we use "gulp serve" to serve the frontend from localhost:5000.
# If you are serving the frontend on a different host/port, change it here.
# This is used to enable cross-origin resource sharing in development.
DEV_FRONTEND_ORIGIN = 'http://localhost:5000'
