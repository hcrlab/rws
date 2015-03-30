#!/usr/bin/env python

from flask import Blueprint
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from websocket import WebsocketServer
import apps
import argparse
import config
import json
import os
import rospy
import secrets
import sys
import threading
import users

app = Flask(__name__, static_folder='dist', static_url_path='')

app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
app_list = app_manager.get_apps()
rws_apps_lock = threading.Lock()
rws_apps_lock.acquire()
rws_apps = {x.package_name(): x for x in app_list}
rws_apps_lock.release()

# Include routes from blueprints
from robot_start_stop import blueprint as robot_start_stop_blueprint
app.register_blueprint(robot_start_stop_blueprint, url_prefix='/api/robot')

from user_presence import blueprint as user_presence_blueprint
app.register_blueprint(user_presence_blueprint,
                       url_prefix='/api/user_presence')

for rws_app in app_list:
    blueprint = Blueprint(
        rws_app.package_name(), __name__,
        static_url_path='/app/{}'.format(rws_app.package_name()),
        static_folder=os.path.join(rws_app.package_path(), 'www'))
    app.register_blueprint(blueprint)

# TODO(jstn): make websocket server url programmatic based on the port number.
# TODO(jstn): randomize port number?
websocket_server = WebsocketServer(9999)
websocket_server.launch()


@app.route('/', methods=['GET', 'POST'])
@users.login_required
def index():
    user, error = users.USER_VERIFIER.check_user(request)
    app_names = [{'id': app.package_name(),
                  'name': app.name()} for app in app_list]
    return render_template('app.html',
                           app_name='Home',
                           app_id='rws_home',
                           app_list=app_names,
                           robot_name=config.ROBOT_NAME,
                           useremail=user.email,
                           username=user.name if user.name is not None else '',
                           server_origin=secrets.SERVER_ORIGIN)


@app.route('/oauth2callback')
def oauth2callback():
    return render_template('oauth2callback.html',
                           BROWSER_API_KEY=secrets.BROWSER_API_KEY)


@app.route('/app/<package_name>')
@users.login_required
def app_controller(package_name):
    if package_name in rws_apps:
        rws_apps_lock.acquire()
        rws_app = rws_apps[package_name]
        rws_app.launch()
        rws_apps_lock.release()

        # For user presence
        user, error = users.USER_VERIFIER.check_user(request)
        # TODO(csu): also add users to user presence set here

        app_names = [{'id': app.package_name(),
                      'name': app.name()} for app in app_list]

        return render_template(
            'app.html',
            app_name=rws_app.name(),
            app_id=package_name,
            app_list=app_names,
            robot_name=config.ROBOT_NAME,
            useremail=user.email,
            username=user.name if user.name is not None else '',
            server_origin=secrets.SERVER_ORIGIN)
    else:
        return 'Error: no app named {}'.format(package_name)


@app.route('/app/close/<package_name>')
@users.login_required
def app_close(package_name):
    if package_name in rws_apps:
        rws_apps_lock.acquire()
        rws_app = rws_apps[package_name]
        if rws_app.is_running():
            rws_app.terminate()
        rws_apps_lock.release()

        # TODO(csu): also remove users from user presence set here

        return redirect(url_for('index'))
    else:
        return 'Error: no app named {}'.format(package_name)


@app.route('/get_websocket_url')
@users.login_required
def websocket_url():
    return secrets.WEBSOCKET_URL


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Robot web server.')
    parser.add_argument('--debug',
                        type=bool,
                        default=False,
                        help='Whether to start the server in debug mode.')
    sys.argv = rospy.myargv()
    args = parser.parse_args()

    app.run(host='0.0.0.0', debug=args.debug)
