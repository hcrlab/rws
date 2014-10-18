from flask import Blueprint
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from identitytoolkit import gitkitclient
import apps
import argparse
import os
import users
import secrets
import threading

app = Flask(__name__)

gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(
  secrets.GITKIT_SERVER_CONFIG_PATH)
user_verifier = users.UserVerifier(gitkit_instance, secrets.ALLOWED_USERS)

app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)
app_list = app_manager.get_apps()
rws_apps_lock = threading.Lock()
rws_apps_lock.acquire()
rws_apps = {x.package_name(): x for x in app_list}
rws_apps_lock.release()

for rws_app in app_list:
  blueprint = Blueprint(rws_app.package_name(), __name__,
      static_url_path='/app/{}'.format(rws_app.package_name()),
      static_folder=os.path.join(rws_app.package_path(), 'www'))
  app.register_blueprint(blueprint)

@app.route('/', methods=['GET', 'POST'])
def index():
  email, error = user_verifier.check_user(request)
  if email is None:
    login_msgs = {
      users.UserVerifierError.NO_COOKIE: 'Log in',
      users.UserVerifierError.INVALID_TOKEN: 'Invalid login',
      users.UserVerifierError.DISALLOWED_USER: 'Only approved users may log in'
    }
    text = ''
    login_msg = login_msgs[error]
    return render_template('login.html', 
      login_msg=login_msg, SERVER_ORIGIN=secrets.SERVER_ORIGIN)

  return render_template('home.html', app_list=app_list,
    current_tab='rws_welcome', SERVER_ORIGIN=secrets.SERVER_ORIGIN)

@app.route('/oauth2callback')
def oauth2callback():
  return render_template('oauth2callback.html',
    BROWSER_API_KEY=secrets.BROWSER_API_KEY)

@app.route('/app/<package_name>')
def app_controller(package_name):
  if package_name in rws_apps:
    rws_apps_lock.acquire()
    rws_app = rws_apps[package_name]
    rws_app.launch()
    rws_apps_lock.release()

    return render_template('app.html', current_tab=package_name, app_list=app_list, rws_app=rws_app)
  else:
    return 'Error: no app named {}'.format(package_name)

@app.route('/app/close/<package_name>')
def app_close(package_name):
  if package_name in rws_apps:
    rws_apps_lock.acquire()
    rws_app = rws_apps[package_name]
    if rws_app.is_running():
      rws_app.terminate()
    rws_apps_lock.release()
    return redirect(url_for('index'))
  else:
    return 'Error: no app named {}'.format(package_name)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Robot web server.')
  parser.add_argument('debug', type=bool, default=False,
      help='Whether to start the server in debug mode.')
  args = parser.parse_args()

  app.run(host='0.0.0.0', debug=args.debug)
