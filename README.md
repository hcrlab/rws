# Robot web server

A web server that runs on a robot running ROS. It provides a platform for people to deploy web apps using [Robot web tools](http://robotwebtools.org/).

RWS is implemented as a Flask website hosted on your robot. Once you log in, you can select from a number of apps to run. An app is a ROS catkin package that has the following:
* An launch/app.launch file.
* A &lt;name&gt; in package.xml
* An &lt;appname&gt; in the &lt;exports&gt; section of package.xml
* A www/ folder with an index.html, and other static HTML, CSS, Javascript, etc.

The server is configured to look in a particular catkin workspace for apps. Any packages that meet the above requirements are assumed to be RWS apps.

## How to make an RWS app
As explained above, an app is a catkin package:
```
cd catkin_ws/src
catkin_create_pkg my_app rospy
```

RWS will use the package name as an internal name for your app. Eventually, people will access your app by going to `http://c1.university.edu/app/my_app`, so just be sure my_app has a suitable name.

You will need to add a human-friendly name with an `<appname>` element in the `<exports>` section of your package.xml:
```html
<exports>
  <appname>My App</appname>
</exports>
```

Create a launch/app.launch file and a www/index.html file:
```
mkdir launch
touch launch/app.launch
mkdir www
touch www/index.html
```

When someone visits your app, and your app isn't already running, RWS will use your launch file by simply running `roslaunch app.launch`. So, your app.launch should include everything that is needed for your app to work, except for the things you expect to already be running on the robot (rosbridge is one of these, see the "Running" instructions below).

You can put any kind of static files in the www/ directory. When a user clicks on your app's name on the website, RWS will inject your index.html into an iframe on the page, and serve any other files in www/ statically.

You can develop your app locally by running your app.launch, launch rosbridge_webserver (see "Running" below), and visiting your index.html. When you want to install it on the robot, just copy it to the catkin_ws on the robot that RWS is monitoring.

## Installing RWS on a robot
RWS runs on Python 2.7

```
cd ~/catkin_ws/src
catkin_create_pkg rws rospy
cd rws/src
git clone git@github.com:hcrlab/rws.git
```

For authentication, you will need to set up the [Google Identity Toolkit](https://developers.google.com/identity-toolkit/quickstart/python). Following the quickstart, you will generate a gitkit-server-config.json, which should be placed in the same folder as main.py. You will also generate a P12 file, which can be saved anywhere. You will reference the location of the P12 file in your gitkit-server-config.json.

You also need to install a few other things.
```
pip install flask
pip install enum34
```

Finally, install [rosbridge_server](http://wiki.ros.org/rosbridge_server) if you don't already have it.

## Configuration
You will need to create a secrets.py file in the same folder as main.py. secrets.py is kept out of this repository, and it may change. However, currently, it needs to contain:
* SERVER_ORIGIN: The protocol, server, and port of the server. For example, `'http://pr2.university.edu:5000'`
* BROWSER_API_KEY: The browser API key from the Google Identity Toolkit instructions (`'AIza...'`)
* ALLOWED_USERS: A list of email addresses of allowed users. As part of the Google Identity Toolkit, you can set up GMail, Yahoo, Facebook, etc. For example, `['user1@gmail.com', 'user2@university.edu']`
* CATKIN_WS: The path to a catkin workspace you'd like to search for apps. For example, `'home/rws/catkin_ws'`

## Running
Run the rosbridge_server:
```
roslaunch rosbridge_server rosbridge_websocket.launch port:=9090
```

Then run the web server:
```
python main.py
```
