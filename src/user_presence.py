from flask import Blueprint, request, jsonify
from sets import Set

blueprint = Blueprint('user_presence', __name__)

current_users = Set()

@blueprint.route('/current', methods=['GET'])
def get_current_users:
    return jsonify(current_users)

@blueprint.route('/add', methods=['POST'])
def add_user():
    user = request.form['user']
    current_users.add(user)

@blueprint.route('/remove', methods=['POST'])
def remove_user():
    user = request.form['user']
    current_users.pop(user)