from enum import Enum
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from functools import wraps
from oauth2client import client, crypt
import secrets


class UserVerifierError(Enum):
    NO_COOKIE = 1
    INVALID_TOKEN = 2
    DISALLOWED_USER = 3


LOGIN_MSGS = {
    UserVerifierError.NO_COOKIE: 'Log in',
    UserVerifierError.INVALID_TOKEN: 'The login was invalid',
    UserVerifierError.DISALLOWED_USER: 'Your email is not registered to use the robot'
}


class UserVerifier(object):
    """Verifies user login using Google API Client Library."""

    def __init__(self):
        pass

    def check_user(self, request):
        """Checks the user login cookie.

    Returns: (user, error), Email is the string email address of the person who
      logged in, or None if the login was invalid. Error is a UserVerifierError
      describing why the login was invalid, or None if the login was valid.
    """
        if 'gtoken' not in request.cookies:
            return None, UserVerifierError.NO_COOKIE
        try:
            token = request.cookies['gtoken']  
            idinfo = client.verify_id_token(token, secrets.GOOGLE_CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return None, UserVerifierError.INVALID_TOKEN
            if idinfo['hd'] != secrets.GOOGLE_APPS_DOMAIN_NAME:
                return None, UserVerifierError.INVALID_TOKEN
        except crypt.AppIdentityError:
            return None, UserVerifierError.INVALID_TOKEN
        return idinfo, None


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
            return redirect(url_for('signin'))
        return f(*args, **kwargs)

    return decorated_function
