from flask import Blueprint
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from user_presence import blueprint as user_presence_blueprint
import config
import os
import rosnode
import secrets
import users


class RobotWebServer(object):
    def __init__(self, app, app_manager, user_verifier, pr2_claimer):
        """Initialize the web server with the given dependencies.
        Args:
          app: The Flask app instance.
          app_manager: The RWS app manager.
          user_verifier: An instance of a UserVerifier.
          pr2_claimer: An instance of Pr2Claimer.
        """
        self._app = app
        self._user_verifier = user_verifier

        # Include routes for each app.
        self._app_manager = app_manager
        self._app_list = app_manager.get_apps()
        self._rws_apps = {x.package_name(): x for x in self._app_list}
        for rws_app in self._app_list:
            blueprint = Blueprint(
                rws_app.package_name(), __name__,
                static_url_path='/app/{}'.format(rws_app.package_name()),
                static_folder=os.path.join(rws_app.package_path(), 'www'))
            self._app.register_blueprint(blueprint)

        # Include routes from blueprints
        self._pr2_claimer = pr2_claimer
        self._app.register_blueprint(pr2_claimer.blueprint(),
                                     url_prefix='/api/robot')
        self._app.register_blueprint(user_presence_blueprint,
                                     url_prefix='/api/user_presence')

        # Set up routes
        self._app.add_url_rule('/signin', 'signin', self.signin)
        self._app.add_url_rule('/app/<package_name>', 'app_controller',
                               self.app_controller)
        self._app.add_url_rule('/app/close/<package_name>', 'app_close',
                               self.app_close)
        self._app.add_url_rule('/get_websocket_url', 'websocket_url',
                               self.websocket_url)
        self._app.add_url_rule('/api/robot/is_started', 'is_started',
                               self.is_started)
        self._app.add_url_rule('/api/web/google_client_id', 'google_client_id', self.google_client_id)
        self._app.add_url_rule('/', 'index', self.index, defaults={'path': 'home'})
        self._app.add_url_rule('/<path>', 'index', self.index)

    @users.login_required
    def index(self, path='home'):
        app_names = [{'id': app.package_name(),
                      'name': app.name()} for app in self._app_list]
        return render_template(
            'app.html',
            route=path,
            google_client_id=secrets.GOOGLE_CLIENT_ID)

    def google_client_id(self):
        return secrets.GOOGLE_CLIENT_ID

    def signin(self):
        return render_template('login.html',
                               client_id=secrets.GOOGLE_CLIENT_ID)

    @users.login_required
    def app_controller(self, package_name):
        if package_name in self._rws_apps:
            rws_app = self._rws_apps[package_name]
            rws_app.launch()

            # For user presence
            user, error = self._user_verifier.check_user(request)
            # TODO(csu): also add users to user presence set here
            app_names = [{'id': app.package_name(),
                          'name': app.name()} for app in self._app_list]

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
            abort(404, 'No app named {}'.format(package_name))

    @users.login_required
    def app_close(self, package_name):
        if package_name in self._rws_apps:
            rws_app = self._rws_apps[package_name]
            if rws_app.is_running():
                rws_app.terminate()

            # TODO(csu): also remove users from user presence set here

            return redirect(url_for('index'))
        else:
            abort(404, 'No app named {}'.format(package_name))

    @users.login_required
    def websocket_url(self):
        return ''

    @users.login_required
    def is_started(self):
        try:
            return '1' if '/robot_state_publisher' in rosnode.get_node_names() else '0'
        except:
            return '0'
