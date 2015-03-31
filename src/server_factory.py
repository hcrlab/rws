from enum import Enum
from flask import Flask
from identitytoolkit import gitkitclient
from robot_web_server import RobotWebServer
from websocket import WebsocketServer
import apps
import users
import secrets


def production():
    """Production server that uses port 9090 for the websocket server.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
    websocket_server = WebsocketServer(9090)
    gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(
        secrets.GITKIT_SERVER_CONFIG_PATH)
    user_verifier = users.UserVerifier(gitkit_instance, secrets.ALLOWED_USERS)
    server = RobotWebServer(app, app_manager, websocket_server, user_verifier)
    return server


def development():
    """Development server that uses port 9999 for the websocket server.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
    websocket_server = WebsocketServer(9999)
    gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(
        secrets.GITKIT_SERVER_CONFIG_PATH)
    user_verifier = users.UserVerifier(gitkit_instance, secrets.ALLOWED_USERS)
    server = RobotWebServer(app, app_manager, websocket_server, user_verifier)
    return server


def test():
    """Test server. Most likely many of the objects will be mocked anyway.
    """
    app = Flask(__name__, static_folder='dist', static_url_path='')
    app_manager = apps.AppManager(catkin_ws=None)
    websocket_server = WebsocketServer(9999)
    user_verifier = users.UserVerifier(None, [])
    server = RobotWebServer(app, app_manager, websocket_server, user_verifier)
    server._app.config['TESTING'] = True
    server._app = server._app.test_client()
    return server
