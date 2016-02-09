from flask import Blueprint
from flask import abort
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from user_presence import blueprint as user_presence_blueprint
import atexit
import config
import os
import rosnode
import secrets
import users


class RobotWebServer(object):
    def __init__(self, app, app_manager, user_manager, robot,
                 websocket_server):
        """Initialize the web server with the given dependencies.
        Args:
          app: The Flask app instance.
          app_manager: The RWS app manager.
          user_manager: An instance of a UserManager.
          user_verifier: An instance of a UserVerifier.
          robot: An instance of Robot.
          websocket_server: An instance of a WebsocketServer
        """
        self._app = app
        self._user_manager = user_manager

        # Start websocket server if needed.
        self._websocket_server = websocket_server
        self._websocket_server.launch()

        # Include routes for each app.
        self._app_manager = app_manager
        self._app_list = app_manager.get_apps()
        self._rws_apps = {x.package_name(): x for x in self._app_list}
        for rws_app in self._app_list:
            blueprint = Blueprint(
                rws_app.package_name(), __name__,
                static_url_path='/a/{}'.format(rws_app.package_name()),
                static_folder=os.path.join(rws_app.package_path(), 'www'))
            self._app.register_blueprint(blueprint)

        # Include routes from blueprints
        self._robot = robot
        self._app.register_blueprint(robot.blueprint(),
                                     url_prefix='/api/robot')
        self._app.register_blueprint(user_presence_blueprint,
                                     url_prefix='/api/user_presence')

        # Set up routes
        self._app.add_url_rule('/', 'index', self.index, defaults={'path': ''})
        self._app.add_url_rule('/signin', 'signin', self.index, defaults={'path': 'signin'})
        self._app.add_url_rule('/app/<path>', 'app', self.index)
        self._app.add_url_rule('/api/users/check_registered', 'check_user',
                               self.check_user)
        self._app.add_url_rule('/api/users/list', 'list_users',
                               self.list_users)
        self._app.add_url_rule('/api/users/update', 'update_user',
                               self.update_user,
                               methods=['POST'])
        self._app.add_url_rule('/api/users/add', 'add_user', self.add_user,
                               methods=['POST'])
        self._app.add_url_rule('/api/users/remove', 'remove_user',
                               self.remove_user,
                               methods=['POST'])
        self._app.add_url_rule('/api/apps/list', 'list_apps', self.list_apps)
        self._app.add_url_rule('/api/app/<package_name>/start', 'start_app',
                               self.start_app,
                               methods=['POST'])
        self._app.add_url_rule('/api/app/<package_name>/close', 'close_app',
                               self.close_app,
                               methods=['POST'])
        self._app.add_url_rule('/api/web/google_client_id', 'google_client_id',
                               self.google_client_id)
        atexit.register(self._app_manager.close_all, self._app_list)

    def index(self, path):
        return self._app.send_static_file('index.html')

    def check_user(self):
        user_count_before = self._user_manager.user_count()
        user, error = self._user_manager.check_user(request)
        if error is not None:
            response = jsonify({'status': 'error', 'error': error})
            response.status_code = 401
            return response
        if user_count_before == 0:
            return jsonify({'status': 'setup'})
        return jsonify({'status': 'success'})

    @users.admin_required
    def add_user(self):
        data = request.get_json()
        if 'email' not in data:
            response = jsonify({'error': 'No email provided.'})
            response.status_code = 400
            return response
        email = data['email']
        is_admin = False
        if 'isAdmin' in data and data['isAdmin'] == True:
            is_admin = True

        user = users.User(email)
        user.is_admin = is_admin
        error = self._user_manager.add_user(user)
        if error is not None:
            response = jsonify({'error': error})
            response.status_code = 400
            return response
        return jsonify({'success': True})

    @users.admin_required
    def remove_user(self):
        data = request.get_json()
        if 'userId' not in data:
            response = jsonify({'error': 'No user ID provided.'})
            response.status_code = 400
            return response
        user_id = data['userId']

        # TODO(jstn): make sure we're not deleting the last admin.

        error = self._user_manager.delete_user(user_id)
        if error is not None:
            response = jsonify({'error': error})
            response.status_code = 400
            return response
        return jsonify({'success': True})

    @users.admin_required
    def update_user(self):
        data = request.get_json()
        if 'userId' not in data:
            response = jsonify({'error': 'No user ID provided.'})
            response.status_code = 400
            return response
        if 'update' not in data:
            response = jsonify({'error': 'No update provided.'})
            response.status_code = 400
            return response
        admins = self._user_manager.list_admins()
        # TODO(jstn): figure out if we're about to remove the last administrator
        #if len(admins) == 1:
        #    response = jsonify({'error': 'Cannot remove last administrator.'})
        #    response.status_code = 400
        #    return response
        prev = self._user_manager.update_user_with_json(data['userId'],
                                                        data['update'])
        if prev is None:
            response = jsonify({'error': 'Invalid user ID.'})
            response.status_code = 400
            return response
        return jsonify({'success': True})

    @users.admin_required
    def list_users(self):
        users = self._user_manager.list_users()
        return jsonify({"data": [user.to_dict() for user in users]})

    def google_client_id(self):
        return secrets.GOOGLE_CLIENT_ID

    @users.login_required
    def list_apps(self):
        data = []
        for package_name, app in self._rws_apps.items():
            data.append({'package_name': package_name, 'app_name': app.name()})

        def sort_by_name_key(app):
            return app['app_name']

        data.sort(key=sort_by_name_key)
        return jsonify({'data': data})

    @users.login_required
    def start_app(self, package_name):
        if package_name in self._rws_apps:
            rws_app = self._rws_apps[package_name]
            rws_app.launch()
            return jsonify({'status': 'success'})
        else:
            response = jsonify({
                'status': 'error',
                'error': 'No app named {}'.format(package_name)
            })
            response.status_code = 401
            return response

    @users.login_required
    def close_app(self, package_name):
        if package_name in self._rws_apps:
            rws_app = self._rws_apps[package_name]
            if rws_app.is_running():
                rws_app.terminate()

            return jsonify({'status': 'success'})
        else:
            response = jsonify({
                'status': 'error',
                'error': 'No app named {}'.format(package_name)
            })
            response.status_code = 401
            return response
