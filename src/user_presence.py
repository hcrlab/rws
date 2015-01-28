from flask import Blueprint, request

blueprint = Blueprint('user_presence', __name__)

@blueprint.route('/remove')
def remove_user():
    user_to_remove = request.form['user']