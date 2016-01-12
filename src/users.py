from bson.objectid import ObjectId
from enum import Enum
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from functools import wraps
from oauth2client import client, crypt
import json
import secrets


class UserVerifierError(Enum):
    NO_COOKIE = 1
    INVALID_TOKEN = 2
    DISALLOWED_USER = 3


LOGIN_MSGS = {
    UserVerifierError.NO_COOKIE: 'User is not signed in.',
    UserVerifierError.INVALID_TOKEN: 'The sign-in was invalid.',
    UserVerifierError.DISALLOWED_USER:
    'User is not registered to use the robot.',
}


def login_required(f):
    """Decorator for view functions that require login.
    
    Assumes that the first argument is an instance (self) that has a
    UserManager as self._user_manager.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        self = args[0]
        user, error = self._user_manager.check_user(request)
        if error is not None:
            response = jsonify({'error': error})
            response.status_code = 401
            return response
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator for view functions that require administrator access.
    
    Assumes that the first argument is an instance (self) that has a
    UserManager as self._user_manager.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        self = args[0]
        user, error = self._user_manager.check_admin(request)
        if error is not None:
            response = jsonify({'error': error})
            response.status_code = 401
            return response
        return f(*args, **kwargs)

    return decorated_function


class User(object):
    def __init__(self, email,
                 mongo_id=None,
                 name=None,
                 is_admin=False,
                 picture=None,
                 locale='en',
                 hosted_domain=None):
        self.mongo_id = None  # Mongo ObjectId
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.picture = picture
        self.locale = locale
        self.hosted_domain = hosted_domain

    def update_with_id_info(self, id_info):
        if 'name' in id_info:
            self.name = id_info['name']
        if 'email' in id_info:
            self.email = id_info['email']
        if 'picture' in id_info:
            self.picture = id_info['picture']
        if 'locale' in id_info:
            self.locale = id_info['locale']
        if 'hd' in id_info:
            self.hosted_domain = id_info['hd']

    @classmethod
    def from_id_info(cls, id_info):
        """Fill out the User from a Google idinfo dictionary.
        """
        if 'email' not in id_info:
            return None
        user = User(id_info['email'])
        cls.update_with_id_info(user, id_info)
        return user

    @staticmethod
    def from_mongo(mongo_user):
        if 'email' not in mongo_user:
            return None
        user = User(mongo_user['email'])
        if '_id' in mongo_user:
            user.mongo_id = ObjectId(mongo_user['_id'])
        if 'name' in mongo_user:
            user.name = mongo_user['name']
        if 'isAdmin' in mongo_user:
            user.is_admin = mongo_user['isAdmin']
        if 'picture' in mongo_user:
            user.picture = mongo_user['picture']
        if 'locale' in mongo_user:
            user.locale = mongo_user['locale']
        if 'hostedDomain' in mongo_user:
            user.hosted_domain = mongo_user['hostedDomain']
        return user

    def to_mongo(self):
        return {
            'name': self.name,
            'email': self.email,
            'isAdmin': self.is_admin,
            'picture': self.picture,
            'hostedDomain': self.hosted_domain
        }

    def to_dict(self):
        return {
            'mongoId': str(self.mongo_id),
            'name': self.name,
            'email': self.email,
            'isAdmin': self.is_admin,
            'picture': self.picture,
        }


class UserManager(object):
    def __init__(self, db):
        self._db = db

    def check_user(self, request):
        """Checks the user signin token.

        Returns: (user, error). user is a User object, error is a string
        describing the authentication error.
        """
        token = None
        if 'gtoken' in request.args:
            token = request.args['gtoken']
        elif 'gtoken' in request.get_json():
            token = request.get_json()['gtoken']
        if token is None:
            return None, 'User is not signed in.'
        try:
            idinfo = client.verify_id_token(token, secrets.GOOGLE_CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com',
                                     'https://accounts.google.com']:
                return None, 'The sign-in was invalid.'
        except crypt.AppIdentityError:
            return None, 'The sign-in was invalid.'

        if 'email' not in idinfo:
            return None, 'The sign-in was invalid.'
        user = self.get_user(idinfo['email'])
        if user is None:
            return None, 'User is not registered to use the robot.'
        user.update_with_id_info(idinfo)
        self.update_user(user.mongo_id, user)

        return user, None

    def check_admin(self, request):
        user, error = self.check_user(request)
        if error is not None:
            return None, error
        if user.is_admin == False:
            return None, 'User is not an administrator.'
        else:
            return user, None

    def add_user(self, user):
        """Registers a new user with the robot.

        A user can be added by an admin with just an email address. Once they
        log in for the first time, the rest of the information is filled in.

        Returns: None if successful, error message if not.
        """
        if user.email is None:
            return 'Cannot add user without email address.'
        if self.get_user(user.email) is not None:
            return 'User already exists.'
        self._db.users.insert_one(user.to_mongo())
        return None

    def list_users(self):
        cursor = self._db.users.find()
        users = []
        for doc in cursor:
            users.append(doc)
        users = [User.from_mongo(x) for x in users]
        return users

    def list_admins(self):
        cursor = self._db.users.find({'isAdmin': True})
        users = []
        for doc in cursor:
            users.append(doc)
        users = [User.from_mongo(x) for x in users]
        return users

    def get_user(self, email):
        user = self._db.users.find_one({'email': email})
        if user is None:
            return None
        return User.from_mongo(user)

    def get_user_by_id(self, user_id):
        user = self._db.users.find_one({'_id': ObjectId(user_id)})
        if user is None:
            return None
        return User.from_mongo(user)

    def update_user(self, user_id, updated_user):
        return self._db.users.find_one_and_update({'_id': ObjectId(user_id)},
                                   {'$set': updated_user.to_dict()})
    def update_user_with_json(self, user_id, updated_user_json):
        return self._db.users.find_one_and_update({'_id': ObjectId(user_id)},
                                   {'$set': updated_user_json})

    def delete_user(self, user_id):
        result = self._db.users.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count == 0:
            return 'User does not exist.'
        return None
