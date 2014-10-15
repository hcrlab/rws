from flask import Flask
from flask import render_template
from flask import request
from identitytoolkit import gitkitclient
import argparse
import secrets

app = Flask(__name__)
gitkit_instance = gitkitclient.GitkitClient.FromConfigFile(
    'gitkit-server-config.json')

@app.route('/', methods=['GET', 'POST'])
def index():
    logged_in = False
    text = ''
    error = ''
    if 'gtoken' in request.cookies:
      gitkit_user = gitkit_instance.VerifyGitkitToken(request.cookies['gtoken'])
      if gitkit_user:
        if gitkit_user.email in secrets.ALLOWED_USERS:
          logged_in = True
          text = 'Welcome, {}!'.format(gitkit_user.email)
        else:
          error = 'You must be approved to log in.'
      else:
        error = 'Invalid login.'
    return render_template('index.html', logged_in=logged_in, text=text,
    error=error, SERVER_ORIGIN=secrets.SERVER_ORIGIN)

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
