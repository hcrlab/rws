from enum import Enum
from flask import Blueprint
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from robot_web_server import RobotWebServer
from websocket import WebsocketServer
from robot_start_stop import Robot
from users import UserManager
import apps
import users
import secrets


def production():
    """Production server that uses port 9090 for the websocket server.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
    client = MongoClient()
    db = client.rws
    user_manager = UserManager(db)
    robot_blueprint = Blueprint('robot', __name__)
    robot = Robot(robot_blueprint, user_manager)
    websocket_server = WebsocketServer(9090)
    server = RobotWebServer(app, app_manager, user_manager, robot,
                            websocket_server)
    return server


def development():
    """Development server.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    cors = CORS(
        app,
        resources={r'/api/*': {'origins': secrets.DEV_FRONTEND_ORIGIN}})
    app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
    client = MongoClient()
    db = client.rws_dev
    user_manager = UserManager(db)
    robot_blueprint = Blueprint('robot', __name__)
    robot = Robot(robot_blueprint, user_manager)
    websocket_server = WebsocketServer(9090)
    server = RobotWebServer(app, app_manager, user_manager, robot,
                            websocket_server)
    return server


def test():
    """Test server. Most likely many of the objects will be mocked anyway.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=None)
    client = MongoClient()
    db = client.rws_test
    user_manager = UserManager(db)
    robot_blueprint = Blueprint('robot', __name__)
    robot = Robot(robot_blueprint, user_manager)
    websocket_server = WebsocketServer(9090)
    server = RobotWebServer(app, app_manager, user_manager, robot,
                            websocket_server)
    server._app.config['TESTING'] = True
    server._app = server._app.test_client()
    return server
