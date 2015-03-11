from enum import Enum
from flask import render_template
from flask import request
from functools import wraps
from identitytoolkit import gitkitclient
import secrets

class UserVerifierError(Enum):
  NO_COOKIE = 1
  INVALID_TOKEN = 2
  DISALLOWED_USER = 3

class UserVerifier(object):
  """Verifies user login using Google Identity Toolkit."""
  def __init__(self, gitkit_client, allowed_users):
    self._gitkit_client = gitkit_client
    self._allowed_users = allowed_users

  def check_user(self, request):
    """Checks the user login cookie.

    Returns: (email, error), Email is the string email address of the person who
      logged in, or None if the login was invalid. Error is a UserVerifierError
      describing why the login was invalid, or None if the login was valid.
    """
    if 'gtoken' not in request.cookies:
      return None, UserVerifierError.NO_COOKIE

    gitkit_user = self._gitkit_client.VerifyGitkitToken(request.cookies['gtoken'])
    if gitkit_user is None:
      return None, UserVerifierError.INVALID_TOKEN

    if gitkit_user.email in self._allowed_users:
      return gitkit_user.email, None
    else:
      return None, UserVerifierError.DISALLOWED_USER

GITKIT_INSTANCE = gitkitclient.GitkitClient.FromConfigFile(
  secrets.GITKIT_SERVER_CONFIG_PATH)
USER_VERIFIER = UserVerifier(GITKIT_INSTANCE, secrets.ALLOWED_USERS)

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    email, error = USER_VERIFIER.check_user(request)
    if email is None:
      login_msgs = {
        UserVerifierError.NO_COOKIE: 'Log in',
        UserVerifierError.INVALID_TOKEN: 'Invalid login',
        UserVerifierError.DISALLOWED_USER: 'Only approved users may log in'
      }
      text = ''
      login_msg = login_msgs[error]

      return render_template(
        'login.html',
        login_msg=login_msg,
        SERVER_ORIGIN=secrets.SERVER_ORIGIN,
      )
    return f(*args, **kwargs)
  return decorated_function

