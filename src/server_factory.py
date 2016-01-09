from enum import Enum
from flask import Blueprint
from flask import Flask
from robot_web_server import RobotWebServer
from websocket import WebsocketServer
from robot_start_stop import Pr2Claimer
import apps
import users
import secrets


def production():
    """Production server that uses port 9090 for the websocket server.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
    user_verifier = users.UserVerifier()
    start_stop_blueprint = Blueprint('robot_start_stop', __name__)
    pr2_claimer = Pr2Claimer(start_stop_blueprint, user_verifier)
    server = RobotWebServer(app, app_manager, user_verifier,
                            pr2_claimer)
    return server


def development():
    """Development server that uses port 9999 for the websocket server.

    We use a different port number because we could be developing on the robot
    itself.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
    user_verifier = users.UserVerifier()
    start_stop_blueprint = Blueprint('robot_start_stop', __name__)
    pr2_claimer = Pr2Claimer(start_stop_blueprint, user_verifier)
    server = RobotWebServer(app, app_manager, user_verifier,
                            pr2_claimer)
    return server


def test():
    """Test server. Most likely many of the objects will be mocked anyway.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=None)
    user_verifier = users.UserVerifier(None, [])
    start_stop_blueprint = Blueprint('robot_start_stop', __name__)
    pr2_claimer = Pr2Claimer(start_stop_blueprint, user_verifier)
    server = RobotWebServer(app, app_manager, user_verifier,
                            pr2_claimer)
    server._app.config['TESTING'] = True
    server._app = server._app.test_client()
    return server
