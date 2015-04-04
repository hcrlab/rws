from enum import Enum
from flask import render_template
from flask import request
from functools import wraps
import secrets


class UserVerifierError(Enum):
    NO_COOKIE = 1
    INVALID_TOKEN = 2
    DISALLOWED_USER = 3


LOGIN_MSGS = {
    UserVerifierError.NO_COOKIE: 'Log in',
    UserVerifierError.INVALID_TOKEN: 'Invalid login',
    UserVerifierError.DISALLOWED_USER: 'Only approved users may log in'
}


class UserVerifier(object):
    """Verifies user login using Google Identity Toolkit."""

    def __init__(self, gitkit_client, allowed_users):
        self._gitkit_client = gitkit_client
        self._allowed_users = allowed_users

    def check_user(self, request):
        """Checks the user login cookie.

    Returns: (user, error), Email is the string email address of the person who
      logged in, or None if the login was invalid. Error is a UserVerifierError
      describing why the login was invalid, or None if the login was valid.
    """
        # TODO(jstn): restore this check when login is enabled.
        user = type('User', (), {'email': 'kb@c1', 'name': 'KB'})()
        return user, None
        #if 'gtoken' not in request.cookies:
        #    return None, UserVerifierError.NO_COOKIE

        #gitkit_user = self._gitkit_client.VerifyGitkitToken(
        #    request.cookies['gtoken'])
        #if gitkit_user is None:
        #    return None, UserVerifierError.INVALID_TOKEN

        #if gitkit_user.email in self._allowed_users:
        #    return gitkit_user, None
        #else:
        #    return None, UserVerifierError.DISALLOWED_USER


def login_required(f):
    """Decorator for view functions that require login.
    
    Assumes that the first argument is an instance (self) that has a
    UserVerifier as self._user_verifier.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        self = args[0]
        user, error = self._user_verifier.check_user(request)
        if user is None:
            text = ''
            login_msg = LOGIN_MSGS[error]
            return render_template('login.html',
                                   login_msg=login_msg,
                                   SERVER_ORIGIN=secrets.SERVER_ORIGIN)
        return f(*args, **kwargs)

    return decorated_function
