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
```xml
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

Your app.launch should push all nodes you need into a namespace named after your app, like so:
```xml
<launch>
  <group ns="say_something">
    <node name="sound_play_tts" pkg="say_something" type="tts_node.py" />
    <node name="sound_play_node" pkg="sound_play" type="soundplay_node.py" />
  </group>
</launch>
```

This prevents your nodes from having a name conflict with another app's nodes, which causes the nodes to shut down.

You can put any kind of static files in the www/ directory. When a user clicks on your app's name on the website, RWS will inject your index.html into an iframe on the page, and serve any other files in www/ statically.

The webserver has an endpoint, `/get_websocket_url`, which you can use to get the websocket URL in your Javascript without hard-coding it. For example, if you're using jQuery, you can get the websocket URL with a GET request:
```js
$.get('/get_websocket_url', function(data, status) {
  var ws_url = data;
  ...
});
```

You can develop your app locally by running your app.launch, launching rosbridge_webserver, and visiting your index.html. When you want to install it on the robot, just copy it to the catkin_ws on the robot that RWS is monitoring and build your package.

## Installing RWS on a robot

### Get the code
RWS runs on Python 2.7. It's recommended that you use ROS Hydro.

```
cd ~/catkin_ws/src
git clone git@github.com:hcrlab/rws.git
```

Ask Justin for a copy of secrets.py, or make your own secrets.py (described below).

### Install requirements
You need to install some Python packages.
```
sudo pip install -r requirements.txt
```

Finally, install [rosbridge_server](http://wiki.ros.org/rosbridge_server) if you don't already have it.
```
sudo apt-get install ros-hydro-rosbridge-suite
```

### Set up user authentication
For user authentication, you will need a private key and config file that works with the [Google Identity Toolkit](https://developers.google.com/identity-toolkit/quickstart/python). You can obtain a copy of one by asking Justin. Or, you can follow their [quickstart guide](https://developers.google.com/identity-toolkit/quickstart/python) and generate your own. Put these files in a location readable by Flask, which you will specify in a secrets.py file. You will also generate a P12 file, which can also be saved anywhere.

Modify gitkit-server-config.json to specify the location of the P12 file. Then, modify secrets.py to specify the location of gitkit-server-config.json. 

### Set up an app.
RWS looks in a particular catkin_ws folder for apps. The location of this folder can be specified in secrets.py (described below), but you will need to create it first. For example:
```
mkdir -p ~/rws/catkin_ws/src
cd ~/rws/catkin_ws/src
catkin_init_workspace
cd ..
catkin_make
```

A sample app you can put in the catkin workspace is [Say something](https://github.com/hcrlab/say_something).
```
cd ~/rws/catkin_ws/src
git clone git@github.com:hcrlab/say_something.git
cd ..
catkin_make
```

Refer to the repo for the app you're installing for further installation instructions.

## Configuration
You will need to create a secrets.py file in the same folder as main.py. secrets.py is kept out of this repository, and it may change. Currently, it must be a file that defines the following constants:
* SERVER_ORIGIN: The protocol, server, and port of the server. For example, `'http://pr2.university.edu:5000'`
* GITKIT_SERVER_CONFIG_PATH: Location on the file system where your gitkit-server-config.json is. For example, `/home/rosie/gitkit/gitkit-server-config.json`
* BROWSER_API_KEY: The browser API key from the Google Identity Toolkit instructions (`'AIza...'`)
* ALLOWED_USERS: A list of email addresses of allowed users. As part of the Google Identity Toolkit, you can set up GMail, Yahoo, Facebook, etc. For example, `['user1@gmail.com', 'user2@university.edu']`
* CATKIN_WS: The path to a catkin workspace you'd like to search for apps. For example, `/home/rosie/rws/catkin_ws`
* WEBSOCKET_URL: The websocket URL for rosbridge (`ws://localhost:9090`)

You can obtain a copy of secrets.py from Justin.

## Running
First, add the catkin workspace that contains all your apps to your ROS package path, if it isn't there already:
```
export ROS_PACKAGE_PATH=/dir/to/rws/catkin_ws:$ROS_PACKAGE_PATH
```
Do this before you running RWS, or just add it to your .bashrc for convenience.

Run `roslaunch rws rws.launch`.
