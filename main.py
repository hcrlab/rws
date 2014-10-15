from flask import Flask
from flask import render_template
from flask import request
from identitytoolkit import gitkitclient
import apps
import argparse
import users
import secrets

app = Flask(__name__)
gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(
  'gitkit-server-config.json')
user_verifier = users.UserVerifier(gitkit_instance, secrets.ALLOWED_USERS)
app_manager = apps.AppManager(catkin_ws=secrets.CATKIN_WS)

@app.route('/', methods=['GET', 'POST'])
def index():
  email, error = user_verifier.check_user(request)
  error_msgs = {
    users.UserVerifierError.NO_COOKIE: 'Log in',
    users.UserVerifierError.INVALID_TOKEN: 'Invalid login',
    users.UserVerifierError.DISALLOWED_USER: 'Only approved users may log in'
  }
  text = ''
  error_msg = ''
  if email is not None:
    text = 'Welcome, {}!'.format(email)
  else:
    error_msg = error_msgs[error]

  app_list = app_manager.get_apps()
  text += ' Your apps are: {}'.format([app.name() for app in app_list])
  return render_template('index.html', logged_in=(email is not None), text=text,
    error=error_msg, SERVER_ORIGIN=secrets.SERVER_ORIGIN)

@app.route('/oauth2callback')
def oauth2callback():
  return render_template('oauth2callback.html',
    BROWSER_API_KEY=secrets.BROWSER_API_KEY)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Robot web server.')
  parser.add_argument('debug', type=bool, default=False,
      help='Whether to start the server in debug mode.')
  args = parser.parse_args()

  app.run(host='0.0.0.0', debug=args.debug)
